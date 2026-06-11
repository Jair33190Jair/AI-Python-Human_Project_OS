#!/usr/bin/env python3
"""Usage: screenshot.py <html_abs_path> <output_png_path> [width] [height]"""
import sys
from playwright.sync_api import sync_playwright

html_path, output_path = sys.argv[1], sys.argv[2]
width, height = int(sys.argv[3]) if len(sys.argv) > 3 else 1440, int(sys.argv[4]) if len(sys.argv) > 4 else 900

def reveal_full_page(page, viewport_height):
    step = max(1, int(viewport_height * 0.8))
    y = 0

    while True:
        page.evaluate("(scroll_y) => window.scrollTo(0, scroll_y)", y)
        page.wait_for_timeout(120)
        page_height = page.evaluate("document.documentElement.scrollHeight")
        if y + viewport_height >= page_height:
            break
        y += step

    page.evaluate("document.querySelectorAll('.reveal').forEach((el) => el.classList.add('in'))")
    page.evaluate(
        """async () => {
            await Promise.all([...document.images].map(async (img) => {
                if (!img.complete) {
                    await new Promise((resolve) => {
                        img.addEventListener('load', resolve, {once: true});
                        img.addEventListener('error', resolve, {once: true});
                    });
                }
                if (img.decode) {
                    await img.decode().catch(() => {});
                }
            }));
        }"""
    )

    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(250)

def stabilize_full_page_capture(page):
    page.evaluate(
        """() => {
            document.querySelectorAll('*').forEach((el) => {
                const position = getComputedStyle(el).position;
                if (position === 'sticky' || position === 'fixed') {
                    el.classList.add('__review_static_position');
                }
            });
        }"""
    )
    page.add_style_tag(
        content="""
            .__review_static_position,
            .nav {
                position: static !important;
            }
        """
    )

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": width, "height": height})
    page.goto(f"file://{html_path}")
    page.wait_for_load_state("networkidle")
    reveal_full_page(page, height)
    stabilize_full_page_capture(page)
    page.screenshot(path=output_path, full_page=True)
    browser.close()

print(f"Screenshot: {output_path}")
