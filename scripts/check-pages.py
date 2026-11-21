#!/usr/bin/env python3
"""Basic quality checks for every HTML page in the site.

For each page (redirect stubs that only forward to another page are skipped):
  - exactly one <title>, and a <meta name="description"> (used by search
    engines, link previews, and this site's own search results)
  - <html lang="...">, and a mobile viewport tag
  - exactly one <h1>
  - no duplicate id="..." values (outside <script> and <pre>), because
    duplicate ids break #anchor links and the table of contents
  - no em dashes (the site style uses " - "; see scripts/remove-em-dashes.ps1)

Usage:
  python3 scripts/check-pages.py            # whole site
  python3 scripts/check-pages.py "AI Engineer"
Exit code is 1 when anything fails, so it can run in CI.
"""
import re
import sys
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent.parent
scan = root / (sys.argv[1] if len(sys.argv) > 1 else ".")

ID = re.compile(r'\bid="([^"]+)"')
problems = []
pages = 0
for html in sorted(scan.rglob("*.html")):
    if ".git" in html.parts:
        continue
    text = html.read_text(encoding="utf-8", errors="replace")
    rel = html.relative_to(root).as_posix()
    if 'http-equiv="refresh"' in text:
        continue  # redirect stub
    pages += 1

    def fail(msg):
        problems.append(f"{rel}: {msg}")

    if len(re.findall(r"<title>[^<]+</title>", text)) != 1:
        fail("needs exactly one non-empty <title>")
    m = re.search(r'<meta name="description" content="([^"]*)"', text)
    if not m or len(m.group(1).strip()) < 20:
        fail('missing or very short <meta name="description">')
    if not re.search(r'<html lang="[^"]+"', text):
        fail('missing <html lang="...">')
    if 'name="viewport"' not in text:
        fail("missing viewport meta tag (page will not scale on phones)")
    h1 = len(re.findall(r"<h1[\s>]", text))
    if h1 != 1:
        fail(f"has {h1} <h1> elements, expected 1")
    body = re.sub(r"<(script|pre)\b[\s\S]*?</\1>", "", text)
    dups = sorted(i for i, c in Counter(ID.findall(body)).items() if c > 1)
    if dups:
        fail(f"duplicate ids: {', '.join(dups)}")
    if "\u2014" in text:
        fail(f"{text.count(chr(0x2014))} em dash(es); use ' - ' instead")

for p in problems:
    print("ERROR:", p)
print(f"Checked {pages} pages: {len(problems)} problem(s)")
sys.exit(1 if problems else 0)
