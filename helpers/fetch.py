#!/usr/bin/env python3
"""
Unified legal URL → markdown extractor.

Usage:
  python fetch.py <URL> [--allow-paid]

stdout:  clean markdown
stderr:  path used (resolver name | "pdf" | "firecrawl")
exit 0:  success
exit 1:  inaccessible / extraction failed
exit 2:  would need Firecrawl (paid) but --allow-paid not set
"""
import sys
from pathlib import Path
from urllib.parse import urlparse

# make resolvers/ and extractors/ importable
sys.path.insert(0, str(Path(__file__).parent))

import requests

from resolvers import fedlex, eurlex, basel_ods
from extractors import pdf

RESOLVERS = [fedlex, eurlex, basel_ods]


def _pdf_content(url: str) -> bytes | None:
    path = urlparse(url).path.lower()
    path_hint = path.endswith(".pdf") or any(
        segment.startswith("pdf") for segment in path.split("/")
    )

    try:
        if not path_hint:
            resp = requests.head(
                url, timeout=10, allow_redirects=True
            )
            ct = resp.headers.get("Content-Type", "")
            path_hint = "pdf" in ct.lower()
            if not path_hint:
                return None

        resp = requests.get(url, timeout=60, allow_redirects=True)
        resp.raise_for_status()
        ct = resp.headers.get("Content-Type", "")
        if (
            path_hint
            or "pdf" in ct.lower()
            or resp.content.startswith(b"%PDF-")
        ):
            return resp.content
    except Exception:
        return None

    return None


def _fetch_firecrawl(url: str) -> str:
    from firecrawl import FirecrawlApp
    app = FirecrawlApp()
    result = app.scrape_url(
        url, params={"formats": ["markdown"]}
    )
    return result.get("markdown", "")


def main() -> None:
    args = sys.argv[1:]
    allow_paid = "--allow-paid" in args
    urls = [a for a in args if not a.startswith("--")]

    if not urls:
        print(
            "Usage: fetch.py <URL> [--allow-paid]",
            file=sys.stderr,
        )
        sys.exit(1)

    url = urls[0]

    for resolver in RESOLVERS:
        if resolver.PATTERN.search(url):
            name = resolver.__name__.rsplit(".", 1)[-1]
            print(name, file=sys.stderr)
            try:
                print(resolver.resolve(url))
            except Exception as e:
                print(f"error: {e}", file=sys.stderr)
                sys.exit(1)
            return

    pdf_bytes = _pdf_content(url)
    if pdf_bytes is not None:
        print("pdf", file=sys.stderr)
        try:
            print(pdf.extract(pdf_bytes, source_url=url))
        except Exception as e:
            print(f"error: {e}", file=sys.stderr)
            sys.exit(1)
        return

    if allow_paid:
        print("firecrawl", file=sys.stderr)
        try:
            print(_fetch_firecrawl(url))
        except Exception as e:
            print(f"error: {e}", file=sys.stderr)
            sys.exit(1)
        return

    print(
        "Cannot extract without Firecrawl (paid). "
        "Re-run with --allow-paid.",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
