"""
Extract all unique same-domain internal links from a URL.
Outputs one absolute URL per line, homepage first.
Usage: python3 extract_links.py <url>
"""
import sys
import urllib.request
import urllib.parse
from html.parser import HTMLParser


class LinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href" and value:
                    self.links.append(value)


def main():
    if len(sys.argv) != 2:
        print("Usage: extract_links.py <url>", file=sys.stderr)
        sys.exit(1)

    base = sys.argv[1].rstrip("/")
    parsed_base = urllib.parse.urlparse(base)
    origin = f"{parsed_base.scheme}://{parsed_base.netloc}"

    req = urllib.request.Request(base, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    extractor = LinkExtractor()
    extractor.feed(html)

    seen = set()
    results = [base]  # homepage always first
    seen.add(base)

    for href in extractor.links:
        href = href.strip()
        if not href or href.startswith("#") or href.startswith("mailto:"):
            continue
        if href.startswith("//"):
            href = parsed_base.scheme + ":" + href
        elif href.startswith("/"):
            href = origin + href
        elif not href.startswith("http"):
            continue

        # same domain only, strip fragment and trailing slash
        p = urllib.parse.urlparse(href)
        if p.netloc != parsed_base.netloc:
            continue
        normalized = f"{p.scheme}://{p.netloc}{p.path}".rstrip("/") or origin
        if normalized not in seen:
            seen.add(normalized)
            results.append(normalized)

    for url in results:
        print(url)


if __name__ == "__main__":
    main()
