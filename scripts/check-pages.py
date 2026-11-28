#!/usr/bin/env python3
"""Basic quality checks for every HTML page in the site.

For each page (redirect stubs that only forward to another page are skipped):
  - exactly one <title>, and a <meta name="description"> (used by search
    engines, link previews, and this site's own search results)
  - <html lang="...">, and a mobile viewport tag
  - exactly one <h1>
  - no duplicate id="..." values (outside <script> and <pre>), because
    duplicate ids break #anchor links and the table of contents
  - no em dashes, as a character or as an &mdash; entity (the site style uses
    " - "; see scripts/remove-em-dashes.ps1)
  - balanced tags: no stray closing tags and no unclosed elements. This also
    catches a raw "<" in text or math, like $x_{<t}$, which the browser reads
    as the start of a tag (write &lt; instead)

Usage:
  python3 scripts/check-pages.py            # whole site
  python3 scripts/check-pages.py "AI Engineer"
Exit code is 1 when anything fails, so it can run in CI.
"""
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

root = Path(__file__).resolve().parent.parent
scan = root / (sys.argv[1] if len(sys.argv) > 1 else ".")

ID = re.compile(r'\bid="([^"]+)"')
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
        "param", "source", "track", "wbr"}
# end tags the HTML spec lets you leave out; a missing one is not an error
OPTIONAL_END = {"p", "li", "td", "th", "tr", "thead", "tbody", "dt", "dd", "option",
                "html", "head", "body"}


class TagBalance(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_startendtag(self, tag, attrs):
        pass  # <br/> style: nothing to close

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                left_open = [f"<{t}> (line {ln})" for t, ln in self.stack[i + 1:] if t not in OPTIONAL_END]
                if left_open:
                    self.errors.append(f"</{tag}> on line {self.getpos()[0]} closes unclosed {', '.join(left_open)}")
                del self.stack[i:]
                return
        self.errors.append(f"stray </{tag}> on line {self.getpos()[0]}")


def tag_errors(text):
    checker = TagBalance()
    checker.feed(text)
    checker.close()
    left_open = [f"<{t}> (line {ln})" for t, ln in checker.stack if t not in OPTIONAL_END]
    if left_open:
        checker.errors.append(f"never closed: {', '.join(left_open)}")
    return checker.errors
problems = []
pages = 0
titles = {}
descriptions = {}
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
    dashes = text.count("\u2014") + len(re.findall(r"&mdash;|&#8212;|&#x2014;", text, re.I))
    if dashes:
        fail(f"{dashes} em dash(es) (character or &mdash; entity); use ' - ' instead")
    for err in tag_errors(text)[:3]:
        fail(f"tag structure: {err}")
    if rel != "404.html":
        if not re.search(r'<link rel="canonical" href="https://[^"]+"', text):
            fail("missing canonical link (run scripts/apply-layout.py)")
        t = re.search(r"<title>([^<]+)</title>", text)
        if t:
            titles.setdefault(t.group(1).strip(), []).append(rel)
        if m:
            descriptions.setdefault(m.group(1).strip(), []).append(rel)

for label, seen in (("title", titles), ("meta description", descriptions)):
    for value, rels in seen.items():
        if len(rels) > 1:
            problems.append(f"same {label} on {len(rels)} pages ({', '.join(rels)}): {value[:70]}")

for p in problems:
    print("ERROR:", p)
print(f"Checked {pages} pages: {len(problems)} problem(s)")
sys.exit(1 if problems else 0)
