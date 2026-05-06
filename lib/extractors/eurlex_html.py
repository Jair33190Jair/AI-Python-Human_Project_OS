"""
Extractor for EUR-Lex CONVEX HTML.

Input:  str — HTML content from eur-lex.europa.eu
Output: markdown string
"""
# deps: beautifulsoup4
import re

from bs4 import BeautifulSoup, Tag


def _doc_title(soup) -> str:
    parts = []
    for p in soup.find_all("p", class_="oj-doc-ti"):
        t = p.get_text(" ", strip=True)
        if t:
            parts.append(t)
    return " — ".join(parts[:2]) if parts else "Unknown"


def _is_list_table(table: Tag) -> bool:
    rows = table.find_all("tr")
    if not rows:
        return False
    return len(rows[0].find_all("td")) == 2


def _table_lines(table: Tag) -> list[str]:
    lines = []
    body = table.find("tbody", recursive=False)
    row_parent = body if body is not None else table
    for row in row_parent.find_all("tr", recursive=False):
        cells = [
            _cell_text(cell)
            for cell in row.find_all("td", recursive=False)
        ]
        cells = [cell for cell in cells if cell]
        if not cells:
            pass
        elif len(cells) == 1:
            lines.append(cells[0])
        else:
            lines.append(
                f"   {cells[0]} {' '.join(cells[1:])}".rstrip()
            )
        for nested in row.find_all("table"):
            lines.extend(_table_lines(nested))
    return lines


def _cell_text(cell: Tag) -> str:
    clone = BeautifulSoup(str(cell), "html.parser")
    for nested in clone.find_all("table"):
        nested.decompose()
    return clone.get_text(" ", strip=True)


def _collect_lines(el: Tag, lines: list[str]) -> None:
    if not isinstance(el, Tag):
        return
    classes = el.get("class") or []
    if "eli-subdivision" in classes:
        return
    if el.name == "p" and "oj-ti-art" in classes:
        return
    if el.name == "p" and "oj-sti-art" in classes:
        return
    if el.name == "p" and "oj-normal" in classes:
        t = el.get_text(" ", strip=True)
        if t:
            lines.append(t)
        return
    if el.name == "p" and any(
        cls.startswith("oj-ti-grseq") for cls in classes
    ):
        t = el.get_text(" ", strip=True)
        if t:
            lines.append(f"### {t}")
        return
    if el.name == "p" and any(
        cls.startswith("oj-sti-grseq") for cls in classes
    ):
        t = el.get_text(" ", strip=True)
        if t:
            lines.append(f"#### {t}")
        return
    if el.name == "table":
        lines.extend(_table_lines(el))
        return
    for child in el.children:
        _collect_lines(child, lines)


def _extract_article(div: Tag) -> str | None:
    num_p = div.find("p", class_="oj-ti-art")
    if not num_p:
        return None

    num = num_p.get_text(strip=True)
    title_p = div.find("p", class_="oj-sti-art")
    title = (
        title_p.get_text(strip=True) if title_p else ""
    )

    header = f"## {num}"
    if title:
        header += f" — {title}"

    lines: list[str] = []
    for child in div.children:
        _collect_lines(child, lines)

    body = "\n\n".join(lines)
    if lines:
        return f"{header}\n\n{body}"
    return header


def _extract_annex(container: Tag) -> str | None:
    titles = [
        p.get_text(" ", strip=True)
        for p in container.find_all("p", class_="oj-doc-ti")
        if p.get_text(" ", strip=True)
    ]
    if not titles:
        return None

    sections = [f"## {titles[0]}"]
    if len(titles) > 1:
        sections.append(f"### {titles[1]}")

    lines: list[str] = []
    for child in container.children:
        _collect_lines(child, lines)

    if lines:
        sections.append("\n\n".join(lines))
    return "\n\n".join(sections)


def extract(content: str, source_url: str = "") -> str:
    soup = BeautifulSoup(content, "html.parser")

    containers = soup.find_all("div", class_="eli-container")
    if not containers:
        containers = [soup]

    for container in containers:
        doc_title = _doc_title(container)

        article_divs = [
            div
            for div in container.find_all(
                "div", class_="eli-subdivision"
            )
            if re.search(
                r"(?:^|\.)art_\d+$",
                div.get("id", ""),
            )
        ]

        if not article_divs:
            continue

        sections = [f"# {doc_title}"]
        for div in article_divs:
            text = _extract_article(div)
            if text:
                sections.append(text)

        annexes = [
            div
            for div in soup.find_all("div", class_="eli-container")
            if re.match(r"anx_", div.get("id", ""))
        ]
        for annex in annexes:
            text = _extract_annex(annex)
            if text:
                sections.append(text)

        md = "\n\n---\n\n".join(sections) + "\n"
        return md

    doc_title = _doc_title(soup)
    raise ValueError(
        f"No EUR-Lex article containers found for {doc_title}"
    )
