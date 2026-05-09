#!/usr/bin/env python3
"""
Form filler using Playwright.

  --inspect <url>           -> JSON field list, stdout (headless)
  --fill <url> <map.json>   -> fill form visually (headful), pauses for review
  --browser <name>          -> chromium (default), chrome, or msedge
  --executable-path <path>  -> launch a local Chrome/Chromium binary
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

_FRAME_COUNT_JS = """() => {
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

# Returns [{label, selector, type, required, name?, value_attr?, options?}]
_INSPECT_JS = """
() => {
  const fields = [];
  const seen = new Set();
  const skip = el => !!el.closest(
    '#onetrust-consent-sdk,[id*=onetrust],[class*=onetrust],' +
    '[id*=consent-sdk],[class*=cookie-banner]'
  );

  function lbl(el) {
    let t = el.getAttribute('aria-label') || '';
    if (!t) {
      const lby = el.getAttribute('aria-labelledby');
      if (lby) t = document.getElementById(lby)?.textContent || '';
    }
    if (!t && el.id)
      t = document.querySelector(`label[for="${el.id}"]`)?.textContent || '';
    if (!t) t = el.closest('label')?.textContent?.replace(el.value || '', '') || '';
    if (!t) t = el.name || el.placeholder || '';
    return t.trim().replace(/\\*+$/, '').trim();
  }

  function sel(el) {
    const tag = el.tagName.toLowerCase();
    const type = (el.type || '').toLowerCase();
    if (el.id) return '#' + el.id;
    if (el.name) {
      if (type === 'radio' || type === 'checkbox')
        return `${tag}[name="${el.name}"][value="${el.value}"]`;
      return `${tag}[name="${el.name}"]`;
    }
    const siblings = [...(el.parentElement?.querySelectorAll(tag) || [])];
    return `${tag}:nth-child(${siblings.indexOf(el) + 1})`;
  }

  const inputs = document.querySelectorAll(
    'input:not([type=hidden]):not([type=submit]):not([type=button]):not([type=reset]),' +
    'select,textarea'
  );

  for (const el of inputs) {
    if (skip(el)) continue;
    const tag = el.tagName.toLowerCase();
    const type = tag === 'select' ? 'select'
               : tag === 'textarea' ? 'textarea'
               : (el.type || 'text').toLowerCase();
    const label = lbl(el);
    const selector = sel(el);
    if (seen.has(selector)) continue;
    seen.add(selector);

    const field = {
      label,
      selector,
      type,
      required: el.required || el.getAttribute('aria-required') === 'true'
    };
    if (type === 'radio' || type === 'checkbox') field.value_attr = el.value;
    if (type === 'radio') field.group = el.name;
    if (type === 'select')
      field.options = [...el.options].map(o => ({ value: o.value, text: o.text.trim() }));

    fields.push(field);
  }
  return fields;
}
"""


async def _best_frame(page):
    """Return the frame with the most non-banner form inputs."""
    best, best_count = page, 0
    for frame in page.frames:
        try:
            count = await frame.evaluate(_FRAME_COUNT_JS)
            if count > best_count:
                best_count, best = count, frame
        except Exception:
            pass
    return best


async def _dismiss_cookies(page) -> None:
    # CSS selector approach first (faster, more reliable)
    for selector in [
        "#onetrust-accept-btn-handler",
        ".onetrust-accept-btn-handler",
        "[id*='accept'][id*='cookie']",
        "[class*='accept'][class*='cookie']",
    ]:
        try:
            await page.wait_for_selector(selector, timeout=2000)
            await page.click(selector, timeout=2000)
            await page.wait_for_timeout(1500)
            return
        except Exception:
            pass
    # Fallback: visible button text
    for text in [
        "Alle Cookies akzeptieren", "Alle zulassen", "Akzeptieren",
        "Accept all", "Accept All",
    ]:
        try:
            await page.get_by_role("button", name=text, exact=True).click(timeout=2000)
            await page.wait_for_timeout(1500)
            return
        except Exception:
            pass


async def _launch_browser(
    playwright, browser_name: str, executable_path: str | None, *, headless: bool
):
    options = {"headless": headless}
    if executable_path:
        options["executable_path"] = executable_path
    elif browser_name != "chromium":
        options["channel"] = browser_name
    return await playwright.chromium.launch(**options)


async def _open_form(
    playwright,
    url: str,
    browser_name: str,
    executable_path: str | None,
    *,
    headless: bool,
):
    browser = await _launch_browser(
        playwright, browser_name, executable_path, headless=headless
    )
    page = await browser.new_page()
    await page.goto(url, wait_until="networkidle", timeout=30000)
    await page.wait_for_timeout(2000)
    await _dismiss_cookies(page)
    await page.wait_for_timeout(3000)
    frame = await _best_frame(page)
    return browser, page, frame


async def inspect(url: str, browser_name: str, executable_path: str | None) -> None:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser, _, frame = await _open_form(
            p, url, browser_name, executable_path, headless=True
        )
        fields = await frame.evaluate(_INSPECT_JS)
        await browser.close()
    print(json.dumps(fields, ensure_ascii=False, indent=2))


async def _apply_action(frame, action: dict) -> None:
    selector = action["selector"]
    field_type = action["type"]
    value = action.get("value")
    if value is None:
        return
    if field_type in ("text", "number", "email", "tel", "textarea"):
        await frame.fill(selector, str(value))
    elif field_type in ("checkbox", "radio") and value:
        await frame.check(selector, force=True)
    elif field_type == "checkbox":
        await frame.uncheck(selector, force=True)
    elif field_type == "select":
        await frame.select_option(selector, value=str(value))


async def _pause_for_review(browser) -> None:
    print("\nForm filled - review in the browser and submit there.", file=sys.stderr)
    print("Press Ctrl+C here to close the browser when done.", file=sys.stderr)
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    await browser.close()


async def fill(
    url: str, mapping_path: str, browser_name: str, executable_path: str | None
) -> None:
    from playwright.async_api import async_playwright
    mapping = json.loads(Path(mapping_path).read_text())

    async with async_playwright() as p:
        browser, page, frame = await _open_form(
            p, url, browser_name, executable_path, headless=False
        )
        for action in mapping:
            try:
                await _apply_action(frame, action)
                await page.wait_for_timeout(200)
            except Exception as e:
                print(f"skip {action['selector']}: {e}", file=sys.stderr)
        await _pause_for_review(browser)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--browser",
        choices=("chromium", "chrome", "msedge"),
        default="chromium",
        help="Playwright browser channel to use.",
    )
    parser.add_argument("--executable-path", help="Local Chrome/Chromium binary.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--inspect", metavar="URL")
    mode.add_argument("--fill", nargs=2, metavar=("URL", "MAP_JSON"))
    args = parser.parse_args()

    if args.inspect:
        asyncio.run(inspect(args.inspect, args.browser, args.executable_path))
        return

    url, mapping_path = args.fill
    asyncio.run(fill(url, mapping_path, args.browser, args.executable_path))


if __name__ == "__main__":
    main()
