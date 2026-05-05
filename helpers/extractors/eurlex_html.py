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
    if el.name == "table" and _is_list_table(el):
        for row in el.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) == 2:
                letter = cells[0].get_text(strip=True)
                text = cells[1].get_text(" ", strip=True)
                if letter or text:
                    lines.append(
                        f"   {letter} {text}".rstrip()
                    )
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

        md = "\n\n---\n\n".join(sections) + "\n"
        return md

    doc_title = _doc_title(soup)
    raise ValueError(
        f"No EUR-Lex article containers found for {doc_title}"
    )
