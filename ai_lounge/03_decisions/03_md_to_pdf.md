# MD → PDF: WeasyPrint vs Pandoc

**Date:** 2026-04-19

## Comparison

| Dimension | WeasyPrint | Pandoc |
|-----------|-----------|--------|
| Dependencies | `pip install` + system libs (cairo/pango) | external binary + optional LaTeX |
| Output quality | Good | Excellent (typography) |
| Styling | CSS in code | LaTeX/DOCX template |
| Markdown input | MD → HTML → PDF | Native |
| Portability | Pure Python | Separate install required |
| Maintainability | Python stack trace, testable | Subprocess, debug on stderr |

## Decision: WeasyPrint

Pipeline already produces Markdown and output is for personal
study — publication-grade typography is not needed. Stays fully
in Python, no external binaries.

## When to use Pandoc instead

- Publication-grade typography required
- Multi-format output (DOCX, EPUB, HTML)
- Pandoc already installed on the system

---
