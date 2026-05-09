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
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

# make resolvers/ and extractors/ importable
sys.path.insert(0, str(Path(__file__).parent))

import requests

from resolvers import fedlex, eurlex, basel_ods
from extractors import pdf

RESOLVERS = [fedlex, eurlex, basel_ods]


def _title_from_markdown(markdown: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    for line in markdown.splitlines():
        if line.startswith("## "):
            return line.removeprefix("## ").strip()
    return "Untitled"


def _yaml_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _with_metadata(
    markdown: str, source_url: str, extraction_method: str = ""
) -> str:
    body = markdown.lstrip()
    title = _title_from_markdown(body)
    method_val = f" {extraction_method}" if extraction_method else ""
    frontmatter = "\n".join(
        [
            "---",
            f"title: {_yaml_string(title)}",
            f"source_url: {_yaml_string(source_url)}",
            f"retrieved_at: {date.today().isoformat()}",
            f"extraction_method:{method_val}",
            "warnings:",
            "extraction_status: success",
            "---",
            "",
        ]
    )
    return frontmatter + body


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


_FORM_EXTRACT_JS = """
() => {
  const lines = [];
  const seen = new Set();

  const BANNER_SEL =
    '#onetrust-consent-sdk,[id*=onetrust],[class*=onetrust],' +
    '[id*=consent-sdk],[class*=cookie-banner],[id*=cookie],[class*=cookie-modal]';

  function inBanner(el) { return !!el.closest(BANNER_SEL); }

  function lbl(el) {
    let t = el.getAttribute('aria-label') || '';
    if (!t) {
      const lby = el.getAttribute('aria-labelledby');
      if (lby) t = document.getElementById(lby)?.textContent || '';
    }
    if (!t && el.id)
      t = document.querySelector(`label[for="${el.id}"]`)?.textContent || '';
    if (!t) t = el.closest('label')?.textContent?.replace(el.value || '', '') || '';
    if (!t) t = el.name || '';
    return t.trim().replace(/\\*+$/, '').trim();
  }

  function req(el) {
    return el.required || el.getAttribute('aria-required') === 'true';
  }

  // title from h1 or first h2
  const title = document.querySelector('h1') || document.querySelector('h2');
  if (title && title.tagName === 'H1') {
    lines.push('# ' + title.textContent.trim()); lines.push('');
  }

  const nodes = document.querySelectorAll(
    'h2,h3,h4,' +
    'input:not([type=hidden]):not([type=submit]):not([type=button]):not([type=reset]),' +
    'select,textarea'
  );

  for (const el of nodes) {
    if (inBanner(el)) continue;
    const tag = el.tagName.toLowerCase();
    if (tag === 'h2') { lines.push(''); lines.push('## ' + el.textContent.trim()); lines.push(''); continue; }
    if (tag === 'h3') { lines.push('### ' + el.textContent.trim()); lines.push(''); continue; }
    if (tag === 'h4') { lines.push('#### ' + el.textContent.trim()); lines.push(''); continue; }
    if (tag === 'input') {
      const type = (el.type || 'text').toLowerCase();
      const l = lbl(el);
      const pfl = req(el) ? ' *(Pflicht)*' : '';
      const key = el.id || (el.name + '|' + l);
      if (seen.has(key)) continue; seen.add(key);
      if (type === 'checkbox') lines.push(`- [ ] ${l}`);
      else if (type === 'radio') lines.push(`- ( ) ${l}`);
      else { lines.push(''); lines.push(`**${l}**${pfl}: ___`); }
      continue;
    }
    if (tag === 'select') {
      const l = lbl(el); const pfl = req(el) ? ' *(Pflicht)*' : '';
      const opts = [...el.options].map(o => o.text.trim()).filter(Boolean);
      lines.push(''); lines.push(`**${l}**${pfl}`);
      opts.forEach(o => lines.push(`- ( ) ${o}`)); continue;
    }
    if (tag === 'textarea') {
      const l = lbl(el); const pfl = req(el) ? ' *(Pflicht)*' : '';
      lines.push(''); lines.push(`**${l}**${pfl}: ___`);
    }
  }
  return lines.join('\\n').trim();
}
"""

_FORM_COUNT_JS = """() => {
  const skip = el => !!el.closest(
    '#onetrust-consent-sdk,[id*=onetrust],[class*=onetrust],' +
    '[id*=consent-sdk],[class*=cookie-banner]'
  );
  const all = document.querySelectorAll(
    'input:not([type=hidden]):not([type=submit]):not([type=button]):not([type=reset]),' +
    'select,textarea'
  );
  return [...all].filter(el => !skip(el)).length;
}"""


def _fetch_playwright(url: str) -> tuple[str, str]:
    import asyncio
    from playwright.async_api import async_playwright

    async def _run() -> tuple[str, str]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)
            # dismiss common cookie banners
            cookie_selectors = [
                "#onetrust-accept-btn-handler",
                ".onetrust-accept-btn-handler",
                "[id*='accept'][id*='cookie']",
                "[class*='accept'][class*='cookie']",
            ]
            dismissed = False
            for selector in cookie_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=2000)
                    await page.click(selector, timeout=2000)
                    await page.wait_for_timeout(1500)
                    dismissed = True
                    break
                except Exception:
                    pass
            if not dismissed:
                # Locator fallback: real browser click by visible text
                for text in [
                    "Alle Cookies akzeptieren",
                    "Alle zulassen",
                    "Akzeptieren",
                    "Accept all",
                    "Accept All",
                ]:
                    try:
                        loc = page.get_by_role("button", name=text, exact=True)
                        await loc.click(timeout=3000)
                        await page.wait_for_timeout(1500)
                        dismissed = True
                        break
                    except Exception:
                        pass

            # Find the frame with the most non-banner form inputs
            best_frame = None
            best_count = 0
            for frame in page.frames:
                try:
                    count = await frame.evaluate(_FORM_COUNT_JS)
                    if count > best_count:
                        best_count = count
                        best_frame = frame
                except Exception:
                    pass

            if best_count > 0 and best_frame is not None:
                text = await best_frame.evaluate(_FORM_EXTRACT_JS)
                method = "playwright-form"
            else:
                text = await page.inner_text("body")
                method = "playwright"

            await browser.close()
            return text, method

    return asyncio.run(_run())


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
                print(_with_metadata(resolver.resolve(url), url, name))
            except Exception as e:
                print(f"error: {e}", file=sys.stderr)
                sys.exit(1)
            return

    pdf_bytes = _pdf_content(url)
    if pdf_bytes is not None:
        print("pdf", file=sys.stderr)
        try:
            print(_with_metadata(
                pdf.extract(pdf_bytes, source_url=url),
                url,
                "pdf",
            ))
        except Exception as e:
            print(f"error: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # Playwright — free headless browser fallback
    try:
        import playwright  # noqa: F401
        text, method = _fetch_playwright(url)
        print(method, file=sys.stderr)
        if text and len(text.split()) >= 50:
            print(_with_metadata(text, url, method))
            return
        print("playwright: too little content, trying next", file=sys.stderr)
    except ImportError:
        print("playwright not installed, skipping", file=sys.stderr)
    except Exception as e:
        print(f"playwright error: {e}, trying next", file=sys.stderr)

    if allow_paid:
        print("firecrawl", file=sys.stderr)
        try:
            print(_with_metadata(_fetch_firecrawl(url), url, "firecrawl"))
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
