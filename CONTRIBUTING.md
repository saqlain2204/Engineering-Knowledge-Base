# Contributing

Thank you for contributing to Engineering Knowledge Base.

## Setup

1. Fork and clone the repository.
2. Open or serve from the **repository root** (the folder that contains `index.html` and `styles.css`).
3. Do not open pages from the `AI Engineer/` folder in isolation; shared assets are at the repo root.

## What to contribute

- New subjects (folder + hub + learn/interview tracks)
- Learn pages (concepts, tradeoffs, short code examples)
- Interview Q&A (`<details>` / `<summary>` blocks)
- Factual fixes, typos, and broken links

## File naming (AI Engineering)

| Type | Pattern | Example |
|------|---------|---------|
| Subject hub | `ai-engineering.html` | `AI Engineer/ai-engineering.html` |
| Learn page | `ai-engineering-{topic}.html` | `ai-engineering-rag.html` |
| Interview page | `ai-engineering-interview-{topic}.html` | `ai-engineering-interview-rag.html` |
| Framework learn | `ai-engineering-frameworks-{name}.html` | `ai-engineering-frameworks-langchain.html` |

Place files in the matching category subfolder under `learn/` or `interview/`.

## Relative paths

| From | `styles.css` | `index.html` |
|------|--------------|--------------|
| Repo root | `styles.css` | `index.html` |
| `AI Engineer/` | `../styles.css` | `../index.html` |
| `AI Engineer/learn/{Category}/` | `../../../styles.css` | `../../../index.html` |
| `AI Engineer/interview/{Category}/` | `../../../styles.css` | `../../../index.html` |
| `AI Engineer/research/` | `../../styles.css` | `../../index.html` |

Load scripts before `search.js`:

```html
<script src="../../../assets/site.js"></script>
<script src="../../../assets/search.js" defer></script>
```

## Search index

After adding or renaming HTML pages:

```powershell
powershell -File scripts/build-search-index.ps1
```

Commit `assets/search-index.js` and `assets/search-index.json`.

## Pull requests

- Keep PRs focused when possible.
- Use plain, accurate language.
- Cite sources for non-obvious claims.
- Update the subject hub when adding topics.
- Avoid em dashes in new prose.

Open an [issue](https://github.com/saqlain2204/Engineering-Knowledge-Base/issues) for questions.
