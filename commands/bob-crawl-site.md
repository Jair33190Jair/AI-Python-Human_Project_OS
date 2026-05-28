---
owner: bob
description: Crawl a homepage, extract all same-domain subpage links, fetch each with /bob-web2md, and write one .md per page to an output folder.
argument-hint: <url> <output_dir>
status: draft
---

# /bob-crawl-site

Crawl a site one level deep: discover internal links from the homepage, fetch each page, and write one `.md` file per page.

**Arguments:** `<url> <output_dir> [--overwrite] [--allow-paid]`
- `url` — homepage to crawl (http/https)
- `output_dir` — folder to write `.md` files into (created if absent)
- `--overwrite` — re-fetch and overwrite existing files
- `--allow-paid` — allow Firecrawl for JS-heavy pages that html2text can't handle

Parse `$ARGUMENTS`: first token starting with `http` is the URL, first token not starting with `--` and not the URL is the output dir.

If URL is missing or does not start with `http`, stop:
```
Blocked: usage: /bob-crawl-site <url> <output_dir>
```

---

## Run the crawler

```bash
~/.claude/lib/.venv/bin/python ~/.claude/commands/bob-crawl-site/crawl.py "$URL" "$OUTPUT_DIR" [--overwrite] [--allow-paid]
```

Pass `--overwrite` and `--allow-paid` through if present in `$ARGUMENTS`.

Print the script's stdout directly as the final output — no reformatting needed.

---

## Hard rules

- Never fabricate content. If a page fails, log it — do not fill in.
- Do not recurse into subpages.
