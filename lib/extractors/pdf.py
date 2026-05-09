"""
Extractor for PDF source files.

Input:  bytes — PDF content
Output: markdown string
"""
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

MIN_TEXT_CHARS = 80


def _run(cmd: list[str]) -> str:
    proc = subprocess.run(
        cmd,
        check=False,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())
    return proc.stdout


def _extract_with_pdftotext(path: Path, mode: str = "raw") -> str:
    if not shutil.which("pdftotext"):
        return ""
    flag = "-layout" if mode == "layout" else "-raw"
    return _run(["pdftotext", flag, str(path), "-"])


def _looks_like_layout_columns(text: str) -> bool:
    """Detect lines where pdftotext joined separate columns."""
    lines = [line.rstrip() for line in text.splitlines()]
    long_gaps = [
        line for line in lines
        if re.search(r"\S\s{8,}\S", line)
    ]
    content_lines = [line for line in lines if line.strip()]
    return bool(content_lines) and len(long_gaps) / len(content_lines) > 0.12


def _extract_with_ocr(path: Path) -> str:
    missing = [
        tool
        for tool in ("pdftoppm", "tesseract")
        if not shutil.which(tool)
    ]
    if missing:
        raise RuntimeError(
            "PDF has no embedded text and OCR tools are "
            f"missing: {', '.join(missing)}"
        )
    lang = _ocr_lang()
    with tempfile.TemporaryDirectory() as tmp:
        prefix = Path(tmp) / "page"
        _run([
            "pdftoppm", "-r", "200", "-png",
            str(path), str(prefix),
        ])
        pages = sorted(Path(tmp).glob("page-*.png"))
        chunks = []
        for page in pages:
            text = _run([
                "tesseract", str(page), "stdout",
                "-l", lang, "--psm", "6",
            ])
            chunks.append(text)
    return "\n\n\f\n\n".join(chunks)


def _ocr_lang() -> str:
    override = os.environ.get("CONTENT_EXTRACTOR_OCR_LANG")
    if override:
        return override
    output = _run(["tesseract", "--list-langs"])
    langs = set(output.splitlines()[1:])
    if {"ita", "eng"}.issubset(langs):
        return "ita+eng"
    if "eng" in langs:
        return "eng"
    return next(iter(langs), "eng")


def _clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _title_from_blocks(blocks: list[str], fallback: str) -> str:
    if not blocks:
        return fallback

    lines = []
    for block in blocks[:8]:
        lines.extend(line.strip() for line in block.splitlines())

    title_lines = []
    for line in lines:
        if not line or line.isdigit():
            continue
        upper = line.upper()
        if re.search(r"\b\d{4}\b", line):
            break
        if upper.startswith(("IL ", "LA ", "DELLA ", "DECRETA")):
            break
        if re.match(r"^(Capitolo|Art\.)\b", line, re.IGNORECASE):
            break
        title_lines.append(line)
        if len(title_lines) >= 8:
            break

    return " ".join(title_lines) if title_lines else fallback


def _split_blocks(page: str) -> list[str]:
    raw_blocks = [
        block.strip()
        for block in re.split(r"\n\s*\n", page)
        if block.strip()
    ]
    blocks = []
    for block in raw_blocks:
        blocks.extend(
            part.strip()
            for part in re.split(
                r"\n\s*(?=Art\.\s*\d+)",
                block,
            )
            if part.strip()
        )
    return blocks


def _article_number(raw: str, previous: int | None) -> str:
    if previous is None or not raw.isdigit():
        return raw
    expected = str(previous + 1)
    if raw.startswith(expected) and raw != expected:
        return expected
    return raw


def _format_paragraph_markers(text: str) -> str:
    text = re.sub(r"^[!''`‘’]\s*", "", text)
    formatted = []
    list_indent: str | None = None
    can_start_letter_list = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            formatted.append("")
            can_start_letter_list = False
            continue

        paragraph = re.match(r"^([0-9]{1,2})(?![0-9.])(\S.*)$", line)
        if paragraph:
            marker, body = paragraph.groups()
            formatted.append(f"**{marker}.** {body}")
            list_indent = None
            can_start_letter_list = body.endswith(":")
            continue

        letter = re.match(r"^([a-z])\)\s*(.*)$", line)
        if letter and (list_indent or can_start_letter_list):
            formatted.append(
                f"   {letter.group(1)}) {letter.group(2)}"
            )
            list_indent = "      "
            can_start_letter_list = False
            continue

        bullet = re.match(r"^[–—-]\s*(.*)$", line)
        if bullet:
            formatted.append(f"      - {bullet.group(1)}")
            list_indent = "        "
            can_start_letter_list = False
            continue

        if list_indent:
            formatted.append(f"{list_indent}{line}")
        else:
            formatted.append(line)
        can_start_letter_list = line.endswith(":")

    return "\n".join(formatted)


def _format_block(
    block: str,
    previous_article: int | None,
) -> tuple[str, int | None]:
    block = block.strip()
    if not block:
        return "", previous_article

    if re.match(r"^Capitolo\b", block, flags=re.IGNORECASE):
        return f"## {block}", previous_article

    article = re.match(
        r"^Art\.\s*([0-9]+[a-zA-Z]*)\s*(.*)$",
        block,
        flags=re.DOTALL,
    )
    if article:
        number = _article_number(
            article.group(1), previous_article,
        )
        rest = article.group(2).strip()
        rest = _format_paragraph_markers(rest)
        header = f"## Art. {number}"
        next_article = (
            int(number) if number.isdigit() else previous_article
        )
        text = f"{header}\n\n{rest}" if rest else header
        return text, next_article

    paragraph = re.match(r"^([0-9]{1,2})(?![0-9.])\s*(\S.*)$", block)
    if paragraph:
        return (
            f"**{paragraph.group(1)}.** {paragraph.group(2)}",
            previous_article,
        )

    if re.match(r"^[a-z]\)\s+\S+$", block):
        return block, previous_article

    return _format_paragraph_markers(block), previous_article


def _is_article_rubric(block: str) -> bool:
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    block = lines[-1] if lines else ""
    if len(block) > 90:
        return False
    if block.startswith(("#", "<!--", "**")):
        return False
    if re.match(r"^\d+(\.\d+)?$", block):
        return False
    return not block.endswith((".", ";", ":", ","))


def _join_blocks(blocks: list[str]) -> str:
    if not blocks:
        return ""

    text = blocks[0]
    for previous, current in zip(blocks, blocks[1:]):
        separator = "\n\n"
        if _is_article_rubric(previous) and current.startswith("## Art."):
            separator = "\n"
        text += separator + current
    return text


def _to_markdown(text: str, fallback_title: str) -> str:
    pages = [_clean_text(page) for page in text.split("\f")]
    pages = [page for page in pages if page]
    blocks = []
    for page in pages:
        blocks.extend(_split_blocks(page))

    doc_title = _title_from_blocks(blocks, fallback_title)
    sections = [f"# {doc_title}"]
    previous_article: int | None = None

    for page_number, page in enumerate(pages, start=1):
        page_blocks = _split_blocks(page)
        formatted = []
        for block in page_blocks:
            if block.strip() == doc_title:
                continue
            text, previous_article = _format_block(
                block, previous_article,
            )
            formatted.append(text)
        formatted = [b for b in formatted if b]
        if formatted:
            sections.append(
                f"<!-- page: {page_number} -->\n\n"
                + _join_blocks(formatted)
            )

    return "\n\n---\n\n".join(sections) + "\n"


def extract(content: bytes, source_url: str = "") -> str:
    with tempfile.NamedTemporaryFile(
        suffix=".pdf", delete=False
    ) as f:
        f.write(content)
        tmp_path = Path(f.name)

    try:
        raw = _extract_with_pdftotext(tmp_path, mode="raw")
        if len(_clean_text(raw)) < MIN_TEXT_CHARS:
            raw = _extract_with_pdftotext(tmp_path, mode="layout")
        elif _looks_like_layout_columns(raw):
            layout = _extract_with_pdftotext(tmp_path, mode="layout")
            if not _looks_like_layout_columns(layout):
                raw = layout
        if len(_clean_text(raw)) < MIN_TEXT_CHARS:
            raw = _extract_with_ocr(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    return _to_markdown(raw, source_url.split("/")[-1] or "document")
