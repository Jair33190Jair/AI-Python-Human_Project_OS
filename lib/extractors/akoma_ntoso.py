"""
Extractor for Akoma Ntoso XML (Fedlex format).

Input:  bytes — XML content from fedlex.admin.ch
Output: markdown string
"""
# deps: lxml
import re

from lxml import etree

NS = "http://docs.oasis-open.org/legaldocml/ns/akn/3.0"
NS_MAP = {"akn": NS}
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
SKIP_TAGS = {f"{{{NS}}}authorialNote"}


def _q(name: str) -> str:
    return f"{{{NS}}}{name}"


def _text(el) -> str:
    if el.tag in SKIP_TAGS:
        return ""
    parts = []
    if el.text:
        t = el.text.strip()
        if t:
            parts.append(t)
    for child in el:
        ct = _text(child)
        if ct:
            parts.append(ct)
        if child.tail:
            t = child.tail.strip()
            if t:
                parts.append(t)
    text = " ".join(parts)
    return re.sub(r"\s+([.;,:!?])", r"\1", text)


def _doc_title(tree) -> str:
    lang_el = tree.find(f".//{_q('FRBRlanguage')}")
    lang = (
        lang_el.get("language", "en")
        if lang_el is not None
        else "en"
    )
    for el in tree.findall(f".//{_q('FRBRname')}"):
        if el.get(XML_LANG) == lang:
            return el.get("value", "")
    dt = tree.find(f".//{_q('docTitle')}")
    return _text(dt).strip() if dt is not None else "Unknown"


def _parse_content(content_el) -> list[str]:
    lines = []
    for child in content_el:
        local = (
            child.tag.split("}")[-1]
            if "}" in child.tag
            else child.tag
        )
        if local == "p":
            t = _text(child).strip()
            if t:
                lines.append(t)
        elif local in ("wrapUp", "intro"):
            t = _text(child).strip()
            if t:
                lines.append(t)
        elif local == "blockList":
            intro = child.find(_q("listIntroduction"))
            if intro is not None:
                t = _text(intro).strip()
                if t:
                    lines.append(t)
            for item in child.findall(_q("item")):
                num_el = item.find(_q("num"))
                p_el = item.find(_q("p"))
                num_t = (
                    _text(num_el).strip()
                    if num_el is not None else ""
                )
                p_t = (
                    _text(p_el).strip()
                    if p_el is not None else ""
                )
                if num_t or p_t:
                    lines.append(
                        f"   {num_t} {p_t}".rstrip()
                    )
    return lines


def _parse_block_list(block_list_el) -> list[str]:
    lines = []
    intro = block_list_el.find(_q("listIntroduction"))
    if intro is not None:
        t = _text(intro).strip()
        if t:
            lines.append(t)
    for item in block_list_el.findall(_q("item")):
        num_el = item.find(_q("num"))
        p_el = item.find(_q("p"))
        num_t = _text(num_el).strip() if num_el is not None else ""
        p_t = _text(p_el).strip() if p_el is not None else ""
        if num_t or p_t:
            lines.append(f"   {num_t} {p_t}".rstrip())
    return lines


def _parse_table(table_el, heading: str = "") -> list[str]:
    rows = []
    for tr in table_el.findall(_q("tr")):
        cells = [
            _text(td).strip()
            for td in tr.findall(_q("td"))
        ]
        cells = [re.sub(r"\s+", " ", cell) for cell in cells]
        if any(cells):
            rows.append(cells)

    if not rows:
        return []

    width = max(len(row) for row in rows)
    rows = [row + [""] * (width - len(row)) for row in rows]
    if width == 3 and re.search(
        r"Staaten|States|territories",
        heading,
        re.I,
    ):
        headers = (
            ["No.", "State / territory", "Remarks"]
            if re.search(r"States|territories", heading, re.I)
            else ["Nr.", "Staat / Gebiet", "Bemerkung"]
        )
    else:
        headers = [f"Spalte {i}" for i in range(1, width + 1)]

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * width) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return ["\n".join(lines)]


def _as_reference(el) -> str:
    for ref in el.findall(f".//{_q('ref')}"):
        text = re.sub(r"\s+", " ", _text(ref)).strip()
        match = re.search(r"\bAS\s+(\d{4})\s+(\d+)\b", text)
        if match:
            return f"AS {match.group(1)} {match.group(2)}"
    return "der amtlichen Veröffentlichung"


def _consultation_note(text: str, reference: str) -> str:
    if "geändert" in text:
        return (
            "Die Änderungen anderer Erlasse sind nicht in diesem "
            f"Dokument abgebildet.\nSie können unter {reference} "
            "konsultiert werden."
        )
    if "Koordination" in text:
        return (
            "Die Koordinationsbestimmungen sind nicht in diesem "
            f"Dokument abgebildet.\nSie können unter {reference} "
            "konsultiert werden."
        )
    return ""


def _roman_heading(roman: str, next_text: str) -> str:
    if roman == "I" and "aufgehoben" in next_text:
        return "**I — Aufgehobene Erlasse**"
    if roman == "II" and "geändert" in next_text:
        return "**II — Geänderte Erlasse**"
    return f"**{roman}**"


def _parse_annex(annex_el) -> str:
    num_el = annex_el.find(
        f".//{_q('container')}[@name='headerOfAnnex']/{_q('block')}"
    )
    num = _text(num_el).strip() if num_el is not None else "Anhang"
    lines = [f"## {num}"]

    body = annex_el.find(_q("mainBody"))
    if body is None:
        return "\n\n".join(lines)

    first_p = body.find(_q("p"))
    if first_p is not None:
        t = _text(first_p).strip()
        if t:
            lines.append(f"*{t}*")

    level = body.find(_q("level"))
    if level is None:
        return "\n\n".join(lines)

    heading_el = level.find(_q("heading"))
    heading = _text(heading_el).strip() if heading_el is not None else ""
    if heading:
        lines.append(f"### {heading}")

    content = level.find(_q("content"))
    if content is None:
        note = _consultation_note(heading, _as_reference(level))
        if note:
            lines.append(note)
        return "\n\n".join(lines)

    children = list(content)
    i = 0
    while i < len(children):
        child = children[i]
        local = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if local == "p":
            t = _text(child).strip()
            if t in {"I", "II", "III", "IV", "V"}:
                next_text = (
                    _text(children[i + 1]).strip()
                    if i + 1 < len(children) else ""
                )
                lines.append(_roman_heading(t, next_text))
            elif t == "…":
                note = _consultation_note(
                    "\n".join(lines),
                    _as_reference(child),
                )
                if note:
                    lines.append(note)
            elif t:
                lines.append(t)
        elif local == "blockList":
            lines.extend(_parse_block_list(child))
        elif local == "table":
            lines.extend(_parse_table(child, "\n".join(lines)))
        i += 1

    return "\n\n".join(lines)


def _parse_article(article_el) -> str:
    num_el = article_el.find(_q("num"))
    head_el = article_el.find(_q("heading"))

    num = _text(num_el).strip() if num_el is not None else ""
    heading = (
        _text(head_el).strip() if head_el is not None else ""
    )

    header = f"## {num}"
    if heading:
        header += f" — {heading}"

    body_lines = []

    intro_el = article_el.find(_q("intro"))
    if intro_el is not None:
        t = _text(intro_el).strip()
        if t:
            body_lines.append(t)

    for para in article_el.findall(_q("paragraph")):
        para_num_el = para.find(_q("num"))
        para_num = (
            _text(para_num_el).strip()
            if para_num_el is not None
            else ""
        )
        content_el = para.find(_q("content"))
        if content_el is None:
            continue
        content_lines = _parse_content(content_el)
        if not content_lines:
            continue
        if para_num:
            content_lines[0] = (
                f"**{para_num}.** {content_lines[0]}"
            )
        body_lines.extend(content_lines)

    body = "\n\n".join(body_lines)
    if body:
        return f"{header}\n\n{body}"
    return ""


def extract(content: bytes, source_url: str = "") -> str:
    # strip browser-injected preamble before XML declaration
    start = content.find(b"<")
    if start > 0:
        content = content[start:]

    tree = etree.fromstring(content)
    doc_title = _doc_title(tree)
    articles = tree.findall(f".//{_q('article')}")
    annexes = tree.findall(f".//{_q('doc')}[@name='annex']")

    sections = [f"# {doc_title}"]
    for article_el in articles:
        text = _parse_article(article_el)
        if text.strip():
            sections.append(text)
    for annex_el in annexes:
        text = _parse_annex(annex_el)
        if text.strip():
            sections.append(text)

    return "\n\n---\n\n".join(sections) + "\n"
