"""
Resolver for gesetzessammlung.bs.ch URLs.

Strategy: URL → systematic number → ODS JSON API → markdown
"""
import re

import requests
from bs4 import BeautifulSoup, Tag

PATTERN = re.compile(
    r"gesetzessammlung\.bs\.ch.+/texts_of_law/([0-9.]+)"
)

_API_URL = (
    "https://data.bs.ch/api/explore/v2.1/catalog/"
    "datasets/100354/records"
)


# ---------------------------------------------------------------------------
# HTML helpers (ported from 01_content_extractor)
# ---------------------------------------------------------------------------

def _clean_text(el: Tag) -> str:
    el = el.__copy__()
    for fn in el.find_all("a", class_="footnote"):
        fn.decompose()
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True))


def _section_text(div: Tag) -> str:
    num_el = div.find(class_="number")
    title_el = div.find(class_="title_text")
    num = _clean_text(num_el) if num_el else ""
    title = _clean_text(title_el) if title_el else ""
    if num and title:
        return f"{num} — {title}"
    return _clean_text(div)


def _article_header(div: Tag) -> str:
    num_div = div.find(class_="article_number")
    title_div = div.find(class_="article_title")

    symbol = ""
    if num_div:
        sym_el = num_div.find(class_="article_symbol")
        n_el = num_div.find(class_="number")
        sym = _clean_text(sym_el) if sym_el else "§"
        num = _clean_text(n_el) if n_el else ""
        symbol = f"{sym} {num}".strip()

    title = ""
    if title_div:
        t = _clean_text(title_div).strip()
        if t and t != "\xa0":
            title = t

    return f"{symbol} — {title}" if title else symbol


def _paragraph_lines(div: Tag) -> list[str]:
    lines = []
    num_el = div.find(class_="number", recursive=False)
    para_num = (
        _clean_text(num_el).strip() if num_el else ""
    )
    text_el = div.find(class_="text_content")
    abrog_el = div.find(class_="abrogation_ellip")

    main_text = ""
    if text_el:
        main_text = _clean_text(text_el).strip()
    elif abrog_el:
        main_text = "…"

    if main_text:
        if para_num:
            lines.append(f"**{para_num}.** {main_text}")
        else:
            lines.append(main_text)
    return lines


def _enumeration_lines(table: Tag) -> list[str]:
    n_td = table.find(class_="number")
    v_td = table.find(class_="left_col")
    label = _clean_text(n_td).strip() if n_td else ""
    value = _clean_text(v_td).strip() if v_td else ""
    line = f"   {label} {value}".rstrip()
    return [line] if line.strip() else []


def _extract_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    title_el = soup.find("h1", class_="title")
    abbr_el = soup.find("h2", class_="abbreviation")
    enact_el = soup.find("div", class_="enactment")
    sysnum_el = soup.find("h1", class_="systematic_number")

    title = _clean_text(title_el) if title_el else "Unknown"
    abbr = _clean_text(abbr_el) if abbr_el else ""
    enact = _clean_text(enact_el) if enact_el else ""
    sysnum = _clean_text(sysnum_el) if sysnum_el else ""

    h1 = title
    if abbr:
        h1 += f" {abbr}"

    meta_lines = []
    if sysnum:
        meta_lines.append(f"**{sysnum}**")
    if enact:
        meta_lines.append(enact)

    doc_header = f"# {h1}"
    if meta_lines:
        doc_header += "\n\n" + "  \n".join(meta_lines)

    sections: list[str] = [doc_header]
    current_article_header: str = ""
    current_paragraphs: list[list[str]] = []

    def flush_article() -> None:
        nonlocal current_article_header, current_paragraphs
        if not current_article_header and not current_paragraphs:
            return
        parts = [f"#### {current_article_header}"]
        for para_lines in current_paragraphs:
            parts.append("\n\n".join(para_lines))
        sections.append("\n\n".join(parts))
        current_article_header = ""
        current_paragraphs = []

    root = soup.body if soup.body else soup
    for el in root.children:
        if not isinstance(el, Tag):
            continue
        classes = el.get("class") or []

        if "level_1" in classes and "title" in classes:
            flush_article()
            sections.append(f"## {_section_text(el)}")
        elif "level_2" in classes and "title" in classes:
            flush_article()
            sections.append(f"### {_section_text(el)}")
        elif "article" in classes:
            flush_article()
            current_article_header = _article_header(el)
        elif "paragraph" in classes:
            lines = _paragraph_lines(el)
            if lines:
                current_paragraphs.append(lines)
        elif "enumeration_item" in classes:
            item_lines = _enumeration_lines(el)
            if item_lines:
                if not current_paragraphs:
                    current_paragraphs.append([])
                current_paragraphs[-1].extend(item_lines)

    flush_article()
    return "\n\n---\n\n".join(sections) + "\n"


# ---------------------------------------------------------------------------
# API fetch
# ---------------------------------------------------------------------------

def _fetch_active_record(systematic_number: str) -> dict:
    params = {
        "where": f'systematic_number="{systematic_number}"',
        "order_by": "version_active_since desc",
        "limit": 100,
    }
    resp = requests.get(_API_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    for record in data.get("results", []):
        if record.get("type") == "version" and record.get("is_active"):
            return record
    for record in data.get("results", []):
        if record.get("type") == "version":
            return record

    raise ValueError(
        f"No version record found for {systematic_number}"
    )


def resolve(url: str) -> str:
    m = PATTERN.search(url)
    systematic_number = m.group(1)

    record = _fetch_active_record(systematic_number)
    html = record.get("gesetzestext_html", "")
    if not html:
        raise ValueError(
            f"No gesetzestext_html in record for {systematic_number}"
        )

    return _extract_html(html)
