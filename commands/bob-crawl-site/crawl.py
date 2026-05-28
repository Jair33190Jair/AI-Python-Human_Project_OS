#!/usr/bin/env python3
"""
Crawl a site one level deep and write one .md per page.

Usage:
  python crawl.py <url> <output_dir> [--overwrite] [--allow-paid] [--workers N]

Filenames use stable numbered prefixes: 00_index.md, 01_slug.md, …
An index file (00_index.md) is always written last with a crawl summary.
"""
import sys
import re
import subprocess
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path


PYTHON = str(Path(__file__).parent.parent.parent / "lib/.venv/bin/python")
FETCH = str(Path(__file__).parent.parent.parent / "lib/fetch.py")
EXTRACT = str(Path(__file__).parent / "extract_links.py")

NON_HTML_EXT = (".pdf", ".pptx", ".docx", ".zip", ".xlsx", ".csv", ".png", ".jpg", ".gif")


def slug(url: str) -> str:
    path = urllib.parse.urlparse(url).path.rstrip("/")
    segment = path.rsplit("/", 1)[-1] if path else ""
    clean = re.sub(r"[^a-z0-9-]", "-", segment.lower()).strip("-") if segment else "index"
    return clean or "index"


def numbered_name(n: int, slug_str: str) -> str:
    return f"{n:02d}_{slug_str}.md"


def fetch_page(url: str, out_path: Path, allow_paid: bool) -> tuple[str, str]:
    """Returns (status, detail): status in 'ok', 'skip', 'fail', 'paid'."""
    if out_path.exists():
        return "skip", out_path.name

    cmd = [PYTHON, FETCH, url]
    if allow_paid:
        cmd.append("--allow-paid")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 2:
        return "paid", url
    if result.returncode != 0 or not result.stdout.strip():
        return "fail", url

    out_path.write_text(result.stdout, encoding="utf-8")
    return "ok", out_path.name


def write_crawl_index(out: Path, base_url: str, entries: list[dict]) -> None:
    ok = [e for e in entries if e["status"] == "ok"]
    paid = [e for e in entries if e["status"] == "paid"]
    fail = [e for e in entries if e["status"] == "fail"]
    skip_e = [e for e in entries if e["status"] == "skip"]

    lines = [
        f"# Crawl Index — {base_url}",
        "",
        f"Crawled: {date.today().isoformat()}  ",
        f"Pages fetched: {len(ok)}  ",
        f"Not fetched (requires Firecrawl): {len(paid)}  ",
        "",
        "---",
        "",
        "## Pages",
        "",
    ]
    for e in sorted(entries, key=lambda x: x["n"]):
        name = e["filename"]
        url = e["url"]
        status = e["status"]
        if status == "ok":
            lines.append(f"- [{name}]({name}) — {url}")
        elif status == "paid":
            lines.append(f"- ~~{name}~~ — {url} *(requires Firecrawl — re-run with --allow-paid)*")
        elif status == "fail":
            lines.append(f"- ~~{name}~~ — {url} *(fetch failed)*")
        elif status == "skip":
            lines.append(f"- [{name}]({name}) — {url} *(skipped, already exists)*")

    if paid:
        lines += [
            "",
            "---",
            "",
            "## Not fetched — Firecrawl required",
            "",
            "These pages returned no content with the free html2text extractor.",
            "Re-run with `--allow-paid` to fetch them.",
            "",
        ]
        for e in paid:
            lines.append(f"- {e['url']}")

    lines.append("")
    index_path = out / "00_crawl_index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    args = sys.argv[1:]
    overwrite = "--overwrite" in args
    allow_paid = "--allow-paid" in args
    workers = 8
    for i, a in enumerate(args):
        if a == "--workers" and i + 1 < len(args):
            workers = int(args[i + 1])
    pos = [a for a in args if not a.startswith("--") and not a.lstrip("-").isdigit()]

    if len(pos) < 2 or not pos[0].startswith("http"):
        print("Usage: crawl.py <url> <output_dir> [--overwrite] [--allow-paid] [--workers N]")
        sys.exit(1)

    base_url, output_dir = pos[0], pos[1]
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Extract links
    result = subprocess.run([sys.executable, EXTRACT, base_url], capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        print(f"Blocked: could not extract links from {base_url}")
        sys.exit(1)

    raw_urls = result.stdout.strip().splitlines()
    # Filter non-HTML resources (keep but mark, skip fetching)
    urls = [u for u in raw_urls if not u.lower().endswith(NON_HTML_EXT)]

    # Assign stable numbered names (order from extract_links, homepage = 01)
    # 00 is reserved for the crawl index
    numbered = [(i + 1, u, numbered_name(i + 1, slug(u))) for i, u in enumerate(urls)]

    tasks_to_run = []
    skipped_existing = []
    for n, u, fname in numbered:
        p = out / fname
        if not overwrite and p.exists():
            skipped_existing.append((n, u, fname))
        else:
            tasks_to_run.append((n, u, out / fname))

    entries: list[dict] = []

    with ThreadPoolExecutor(max_workers=workers) as pool:
        future_map = {pool.submit(fetch_page, u, p, allow_paid): (n, u, p) for n, u, p in tasks_to_run}
        for future in as_completed(future_map):
            n, u, p = future_map[future]
            status, detail = future.result()
            entries.append({"n": n, "status": status, "url": u, "filename": p.name})

    for n, u, fname in skipped_existing:
        entries.append({"n": n, "status": "skip", "url": u, "filename": fname})

    write_crawl_index(out, base_url, entries)

    # Print summary
    ok = [e for e in entries if e["status"] == "ok"]
    fail = [e for e in entries if e["status"] == "fail"]
    skip_e = [e for e in entries if e["status"] == "skip"]
    paid = [e for e in entries if e["status"] == "paid"]

    sorted_entries = sorted(entries, key=lambda x: x["n"])
    print(f"\nCrawled: {len(ok)} pages → {output_dir}")
    for e in sorted_entries:
        s, name, u = e["status"], e["filename"], e["url"]
        if s == "ok":
            print(f"  ✓ {name}")
        elif s == "skip":
            print(f"  ~ {name}  (skipped, exists)")
        elif s == "fail":
            print(f"  ✗ {name}  (fetch failed)")
        elif s == "paid":
            print(f"  $ {name}  (Firecrawl required)")
    print(f"  + 00_crawl_index.md")

    if paid:
        print(f"\n  Re-run with --allow-paid to fetch {len(paid)} Firecrawl page(s).")


if __name__ == "__main__":
    main()