<p align="center">
  <img src="assets/logo.svg" width="96" height="96" alt="Engineering Knowledge Base logo">
</p>

<h1 align="center">Engineering Knowledge Base</h1>

<p align="center">
  Static HTML notes and interview Q&amp;A for engineering topics.
</p>

<p align="center">
  <a href="https://engineering.msaqlain.com">Live site</a>
  ·
  <a href="https://github.com/saqlain2204/Engineering-Knowledge-Base">GitHub</a>
  ·
  <a href="https://github.com/saqlain2204/Engineering-Knowledge-Base/issues">Issues</a>
</p>

<p align="center">
  <a href="https://github.com/saqlain2204">@saqlain2204</a>
</p>

## Overview

Engineering Knowledge Base is a static learning site organized by subject. Each subject typically includes:

| Track | Description |
|-------|-------------|
| **Learn** | Reference notes with concepts, tradeoffs, and code snippets |
| **Interview Prep** | Expandable Q&amp;A using HTML `<details>` elements |
| **Research** | Selected paper breakdowns (where available) |

Pages use relative links and work locally or on any static host. Site search uses fuzzy matching over a generated index.

## Quick start

Clone the repository and open `index.html`, or serve the repo root:

```bash
git clone https://github.com/saqlain2204/Engineering-Knowledge-Base.git
cd Engineering-Knowledge-Base
python -m http.server 8080
```

Open [http://localhost:8080](http://localhost:8080).

**Important:** Open the repository root (`Engineering-Knowledge-Base/`), not the `AI Engineer/` folder alone. Shared assets (`styles.css`, `assets/`) live at the repo root.

## Content

### AI Engineering

| Track | Path | Pages |
|-------|------|------:|
| Hub | [`AI Engineer/ai-engineering.html`](AI%20Engineer/ai-engineering.html) | 1 |
| Learn | [`AI Engineer/learn/`](AI%20Engineer/learn/) | 26 |
| Interview | [`AI Engineer/interview/`](AI%20Engineer/interview/) | 23 |
| Research | [`AI Engineer/research/`](AI%20Engineer/research/) | 2 |

Topics are grouped by category (for example `Training-Pipeline/`, `Prompting-and-Retrieval/`).

## Project structure

```
Engineering-Knowledge-Base/
├── index.html
├── styles.css
├── assets/
│   ├── logo.svg
│   ├── site.js              # Path normalization for local browsing
│   ├── search.js            # Fuzzy site search
│   ├── search-index.js      # Generated index (commit with content changes)
│   └── search-index.json
├── scripts/
│   └── build-search-index.ps1
└── AI Engineer/
    ├── ai-engineering.html
    ├── index.html           # Redirects to subject hub
    ├── learn/
    ├── interview/
    └── research/
```

## Tech stack

| Layer | Choice |
|-------|--------|
| Markup | HTML5 |
| Styling | CSS (`styles.css`) |
| Search | Vanilla JS (`assets/search.js`, no bundler) |
| Hosting | Static file server |

## Search index

After adding or renaming pages:

```powershell
powershell -File scripts/build-search-index.ps1
```

Commit the updated `assets/search-index.js` and `assets/search-index.json` with your changes.

## Contributing

1. Fork the repository.
2. Create a branch (for example `add-eval-interview-questions`).
3. Match existing page structure: breadcrumbs, relative paths, footer links.
4. Regenerate the search index if pages changed.
5. Open a pull request against `main`.

See [CONTRIBUTING.md](CONTRIBUTING.md) for path conventions and file naming.

## Deployment

Deploy the repository root to GitHub Pages, Cloudflare Pages, Netlify, or similar. No build step is required.

Production site: [https://engineering.msaqlain.com](https://engineering.msaqlain.com)

## License

No `LICENSE` file is in the repository yet. Contact the maintainer on GitHub for reuse questions.

## Acknowledgments

Maintained by [@saqlain2204](https://github.com/saqlain2204). External sources cited on learn pages belong to their respective authors.
