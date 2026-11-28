#!/usr/bin/env python3
"""Write the shared layout into every page of the static site.

For each HTML page (redirect stubs are skipped) this script writes, between
marker comments so it can run again safely:

  <head>   theme setup (no flash of the wrong theme), canonical URL, Open Graph
           and Twitter card tags, and JSON-LD structured data (WebSite on the
           home page, TechArticle on article pages, BreadcrumbList everywhere)
  <body>   the sticky top bar: logo, main sections, menu button, theme toggle
  footer   the shared site footer (replaces the page's <footer>)

Usage:
  python3 scripts/apply-layout.py           # write
  python3 scripts/apply-layout.py --check   # CI: exit 1 if any page is stale
"""
import html as htmllib
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://engineering.msaqlain.com"
SITE_NAME = "Engineering Knowledge Base"
OG_IMAGE = SITE_URL + "/assets/og-image.png"
AUTHOR = {"@type": "Person", "name": "Mohammed Saqlain", "url": "https://github.com/saqlain2204"}

NAV = [
    ("AI Engineering", "AI Engineer/ai-engineering.html", lambda r: r.startswith("AI Engineer/") and "/research/" not in r),
    ("CS Fundamentals", "CS-Fundamentals/cs-fundamentals.html", lambda r: r.startswith("CS-Fundamentals/")),
    ("Docker &amp; K8s", "Docker-Kubernetes/docker-kubernetes.html", lambda r: r.startswith("Docker-Kubernetes/")),
    ("Graph ML", "Graph ML/graph-ml.html", lambda r: r.startswith("Graph ML/") and "/research/" not in r),
    ("Labs", "Interactive Labs/index.html", lambda r: r.startswith("Interactive Labs/")),
    ("Research", "AI Engineer/research/research-hub.html", lambda r: "/research/" in r),
]

HEAD_S, HEAD_E = "<!-- layout:head:start -->", "<!-- layout:head:end -->"
TOP_S, TOP_E = "<!-- layout:topbar:start -->", "<!-- layout:topbar:end -->"

THEME_SCRIPT = (
    "<script>(function(){var d=document.documentElement,t;d.classList.add('js');"
    "try{t=localStorage.getItem('ekb-theme')}catch(e){}"
    "if(t!=='light'&&t!=='dark'){t=window.matchMedia&&matchMedia('(prefers-color-scheme: light)').matches?'light':'dark'}"
    "d.setAttribute('data-theme',t)})();</script>"
)

MOON = ('<svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>')
SUN = ('<svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
       'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4.5"/>'
       '<path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>')
MENU = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>')


def pages():
    for p in sorted(ROOT.rglob("*.html")):
        if ".git" in p.parts:
            continue
        text = p.read_text(encoding="utf-8")
        if 'http-equiv="refresh"' in text:
            continue
        yield p, text


def url_for(rel: str) -> str:
    return SITE_URL + "/" if rel == "index.html" else SITE_URL + "/" + quote(rel, safe="/")


def strip_tags(s: str) -> str:
    return htmllib.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s))).strip()


def breadcrumbs(page: Path, rel: str, text: str, title: str):
    m = re.search(r'<nav aria-label="Breadcrumb">\s*<p>([\s\S]*?)</p>', text)
    items = []
    if m:
        parts = re.split(r"&rsaquo;|\u203a", m.group(1))
        for part in parts:
            a = re.search(r'<a href="([^"]+)">([\s\S]*?)</a>', part)
            if a:
                href = a.group(1)
                if href.startswith("/"):
                    target = (ROOT / unquote(href.lstrip("/"))).resolve()
                else:
                    target = (page.parent / unquote(href)).resolve()
                try:
                    trel = target.relative_to(ROOT).as_posix()
                except ValueError:
                    continue
                items.append((strip_tags(a.group(2)), url_for(trel)))
            else:
                name = strip_tags(part)
                if name:
                    items.append((name, url_for(rel)))
    else:
        items = [("Home", url_for("index.html"))]
        if rel != "index.html":
            items.append((title, url_for(rel)))
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)
        ],
    }


def head_block(page: Path, rel: str, text: str) -> str:
    title_m = re.search(r"<title>([^<]+)</title>", text)
    title_attr = title_m.group(1).strip() if title_m else SITE_NAME
    title = htmllib.unescape(title_attr)
    desc_m = re.search(r'<meta name="description" content="([^"]*)"', text)
    desc_attr = desc_m.group(1) if desc_m else ""
    desc = htmllib.unescape(desc_attr)
    h1_m = re.search(r"<h1[^>]*>([\s\S]*?)</h1>", text)
    headline = strip_tags(h1_m.group(1)) if h1_m else title

    lines = [HEAD_S, "  " + THEME_SCRIPT,
             '  <meta name="color-scheme" content="dark light">',
             '  <meta name="theme-color" content="#07090d" media="(prefers-color-scheme: dark)">',
             '  <meta name="theme-color" content="#f6f7fb" media="(prefers-color-scheme: light)">']
    if page.name == "404.html":
        lines.append("  " + HEAD_E)
        return "\n".join(lines)

    url = url_for(rel)
    is_article = "/learn/" in rel and page.parent.name != "learn" or "/research/" in rel and not rel.endswith("-hub.html") \
        or rel.startswith("Interactive Labs/") and page.name != "index.html" or "/cheatsheets/" in rel and not rel.endswith("cheatsheets.html") \
        or "/formulas/" in rel
    og_type = "article" if is_article else "website"
    lines += [
        f'  <link rel="canonical" href="{url}">',
        f'  <meta property="og:site_name" content="{SITE_NAME}">',
        f'  <meta property="og:type" content="{og_type}">',
        f'  <meta property="og:title" content="{title_attr}">',
        f'  <meta property="og:description" content="{desc_attr}">',
        f'  <meta property="og:url" content="{url}">',
        f'  <meta property="og:image" content="{OG_IMAGE}">',
        '  <meta property="og:image:width" content="1200">',
        '  <meta property="og:image:height" content="630">',
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{title_attr}">',
        f'  <meta name="twitter:description" content="{desc_attr}">',
        f'  <meta name="twitter:image" content="{OG_IMAGE}">',
    ]
    graph = []
    if rel == "index.html":
        graph.append({"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL + "/", "description": desc,
                      "inLanguage": "en", "author": AUTHOR})
    elif is_article:
        kind = "LearningResource" if rel.startswith("Interactive Labs/") else "TechArticle"
        art = {"@type": kind, "headline": headline, "name": title, "description": desc, "url": url,
               "mainEntityOfPage": url, "inLanguage": "en", "image": OG_IMAGE, "author": AUTHOR,
               "publisher": AUTHOR, "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL + "/"}}
        if kind == "LearningResource":
            art["learningResourceType"] = "Interactive lab"
            art["isAccessibleForFree"] = True
        graph.append(art)
    else:
        graph.append({"@type": "CollectionPage", "name": title, "description": desc, "url": url, "inLanguage": "en",
                      "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL + "/"}})
    graph.append(breadcrumbs(page, rel, text, headline))
    data = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    data = data.replace("</", "<\\/")
    lines.append(f'  <script type="application/ld+json">{data}</script>')
    lines.append("  " + HEAD_E)
    return "\n".join(lines)


def prefix_for(page: Path) -> str:
    if page.name == "404.html":
        return "/"
    rel = os.path.relpath(ROOT, page.parent).replace(os.sep, "/")
    return "" if rel == "." else rel + "/"


def topbar_block(page: Path, rel: str) -> str:
    pre = prefix_for(page)
    links = []
    for label, target, active in NAV:
        cur = ' aria-current="page"' if rel == target else (' aria-current="true"' if active(rel) else "")
        links.append(f'      <a href="{pre}{target}"{cur}>{label}</a>')
    return "\n".join([
        TOP_S,
        '<div class="topbar">',
        '  <div class="topbar-inner">',
        f'    <a class="topbar-brand" href="{pre}index.html" aria-label="{SITE_NAME} home">'
        f'<img src="{pre}assets/logo.svg" alt="" width="30" height="30"><span>Engineering<b>KB</b></span></a>',
        f'    <button class="icon-btn topbar-menu" type="button" aria-expanded="false" aria-controls="topbar-nav" aria-label="Open menu">{MENU}</button>',
        '    <nav class="topbar-nav" id="topbar-nav" aria-label="Main">',
        *links,
        "    </nav>",
        f'    <button class="icon-btn theme-toggle" type="button" aria-label="Switch color theme" title="Switch color theme">{MOON}{SUN}</button>',
        "  </div>",
        "</div>",
        TOP_E,
    ])


def footer_block(page: Path) -> str:
    pre = prefix_for(page)
    items = [(label, pre + target) for label, target, _ in NAV]
    items += [("GitHub", "https://github.com/saqlain2204/Engineering-Knowledge-Base"),
              ("Contribute", "https://github.com/saqlain2204/Engineering-Knowledge-Base/blob/main/CONTRIBUTING.md")]
    lis = "\n".join(
        f'      <li><a href="{h}"{" rel=\"noopener noreferrer\"" if h.startswith("http") else ""}>{l}</a></li>'
        for l, h in items)
    return "\n".join([
        "<footer>",
        '  <div class="site-footer-inner">',
        '    <div class="site-footer-brand">',
        f'      <a class="topbar-brand" href="{pre}index.html"><img src="{pre}assets/logo.svg" alt="" width="30" height="30"><span>Engineering<b>KB</b></span></a>',
        '      <p>Free, beginner-friendly guides to AI, systems, and infrastructure, with worked examples and interactive labs. '
        'Maintained by <a href="https://github.com/saqlain2204" rel="noopener noreferrer">@saqlain2204</a>.</p>',
        "    </div>",
        '    <ul class="site-footer-links">',
        lis,
        "    </ul>",
        "  </div>",
        "</footer>",
    ])


def apply(page: Path, text: str) -> str:
    rel = page.relative_to(ROOT).as_posix()
    # head
    text = re.sub(r"[ \t]*" + re.escape(HEAD_S) + r"[\s\S]*?" + re.escape(HEAD_E) + r"\n?", "", text)
    text = text.replace("</head>", "  " + head_block(page, rel, text) + "\n</head>", 1)
    # top bar
    text = re.sub(re.escape(TOP_S) + r"[\s\S]*?" + re.escape(TOP_E) + r"\n?", "", text)
    text = re.sub(r"(<body[^>]*>\n?)", lambda m: m.group(1) + topbar_block(page, rel) + "\n", text, count=1)
    # footer
    if "<footer>" in text:
        text = re.sub(r"[ \t]*<footer>[\s\S]*?</footer>", footer_block(page), text, count=1)
    return text


def main() -> int:
    check = "--check" in sys.argv
    stale = []
    for page, text in pages():
        new = apply(page, text)
        if new != text:
            stale.append(page.relative_to(ROOT).as_posix())
            if not check:
                page.write_text(new, encoding="utf-8")
    if check:
        for s in stale:
            print("stale layout:", s)
        print(f"{len(stale)} page(s) with a stale layout")
        return 1 if stale else 0
    print(f"Updated layout on {len(stale)} page(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
