# Contributing

Thank you for contributing to Engineering Knowledge Base.

## Setup

1. Fork and clone the repository.
2. Open or serve from the **repository root** (the folder that contains `index.html` and `styles.css`).
3. Do not open pages from the `AI Engineer/` folder in isolation; shared assets are at the repo root.

## What to contribute

- New subjects (folder + hub + learn track)
- Learn pages (concepts, worked examples, short code examples)
- Interactive labs (one HTML file in `Interactive Labs/`, plain JavaScript, using `assets/labs.css`)
- Architecture diagrams (add them to `scripts/diagrams.py`)
- Factual fixes, typos, and broken links

## File naming (AI Engineering)

| Type | Pattern | Example |
|------|---------|---------|
| Subject hub | `ai-engineering.html` | `AI Engineer/ai-engineering.html` |
| Learn page | `ai-engineering-{topic}.html` | `ai-engineering-rag.html` |
| Framework learn | `ai-engineering-frameworks-{name}.html` | `ai-engineering-frameworks-langchain.html` |

Place files in the matching category subfolder under `learn/`.

## Relative paths

| From | `styles.css` | `index.html` |
|------|--------------|--------------|
| Repo root | `styles.css` | `index.html` |
| `AI Engineer/` | `../styles.css` | `../index.html` |
| `AI Engineer/learn/{Category}/` | `../../../styles.css` | `../../../index.html` |
| `Interactive Labs/` | `../styles.css` | `../index.html` |
| `AI Engineer/research/` | `../../styles.css` | `../../index.html` |

Load scripts before `search.js`:

```html
<script src="../../../assets/site.js"></script>
<script src="../../../assets/search.js" defer></script>
```

## Search index

After adding or renaming HTML pages:

```bash
python3 scripts/build-search-index.py
```

Commit `assets/search-index.js`, `assets/search-index.json`, `sitemap.xml`, `robots.txt`, and `llms.txt`. Do not edit them by hand. Then check links:

```bash
python3 scripts/check-links.py
```

If you added a page to a track with a suggested reading order (CS Fundamentals Learn, Docker & Kubernetes Learn), add it to `TRACKS` in `scripts/update-prev-next.py` and to the hub's "Suggested reading order" list in the same position, then write the Previous / Next links:

```bash
python3 scripts/update-prev-next.py
```

Finally, check page basics (one `<title>`, a `<meta name="description">`, a viewport tag, one `<h1>`, no duplicate ids, no em dashes):

```bash
python3 scripts/check-pages.py
```

## Shared layout, theme, and SEO tags

Do not copy the top bar, footer, or head tags by hand. Give the page a `<title>`, a `<meta name="description">`, a breadcrumb `<nav class="breadcrumb">`, and an empty `<footer></footer>`, then run:

```bash
python3 scripts/apply-layout.py
```

It adds the theme script (no flash of the wrong theme), canonical URL, Open Graph and Twitter tags, JSON-LD (TechArticle or LearningResource plus BreadcrumbList), the top bar with the theme toggle, and the footer.

Colors must come from the CSS variables in `styles.css` so both themes work. Check new pages in light and dark mode.

## Diagrams

Add diagrams to `scripts/diagrams.py` and run `python3 scripts/diagrams.py`. It refuses to write a diagram whose text does not fit, whose boxes overlap, or whose arrows do not land on a box edge.

## CI

The `site-checks` GitHub Actions workflow runs all of these on every pull request. It fails if the committed search index or other generated files are stale, the shared layout or a diagram is out of date, any internal link is broken, a reading-order block or hub list is out of date (`update-prev-next.py --check`), or a page fails the basics check.

## Pull requests

- Keep PRs focused when possible.
- Use plain, accurate language.
- Cite sources for non-obvious claims.
- Update the subject hub when adding topics.
- If the new page belongs to a track's suggested reading order (for example CS Fundamentals), add it to `scripts/update-prev-next.py` and run `python3 scripts/update-prev-next.py`.
- Avoid em dashes in new prose.

Open an [issue](https://github.com/saqlain2204/Engineering-Knowledge-Base/issues) for questions.
