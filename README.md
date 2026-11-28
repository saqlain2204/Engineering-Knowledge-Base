<p align="center">
  <img src="assets/logo.svg" width="96" height="96" alt="Engineering Knowledge Base logo">
</p>

<h1 align="center">Engineering Knowledge Base</h1>

<p align="center">
  Free, beginner-friendly guides and interactive labs for AI engineering, CS fundamentals, Docker and Kubernetes, and graph ML.
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
| **Learn** | Guides with concepts, worked examples, diagrams, and code snippets |
| **Interactive Labs** | Small in-browser simulators you can poke (see below) |
| **Research** | Selected paper breakdowns and book-length references (where available) |

Pages use relative links and work locally or on any static host. Every page has a light and a dark theme (it follows your system setting until you pick one with the toggle in the top bar). Site search uses fuzzy matching over a generated index.

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
| Learn | [`AI Engineer/learn/`](AI%20Engineer/learn/) | 34 |
| Research | [`AI Engineer/research/`](AI%20Engineer/research/) | 2 |

Topics are grouped by category (for example `Training-Pipeline/`, `Prompting-and-Retrieval/`). The learn hub has a suggested reading order from classical ML to LLM apps, and pages on it have Previous / Next links.

### CS Fundamentals

| Track | Path | Pages |
|-------|------|------:|
| Hub | [`CS-Fundamentals/cs-fundamentals.html`](CS-Fundamentals/cs-fundamentals.html) | 1 |
| Learn | [`CS-Fundamentals/learn/`](CS-Fundamentals/learn/) | 27 |

Operating systems, databases, and computer networks from zero, grouped by subject (`Operating-Systems/`, `Databases/`, `Computer-Networks/`), plus end-to-end walkthroughs in `Scenarios/`. Pages in the suggested reading order have Previous / Next links, written by `scripts/update-prev-next.py`.

### Docker & Kubernetes

| Track | Path | Pages |
|-------|------|------:|
| Hub | [`Docker-Kubernetes/docker-kubernetes.html`](Docker-Kubernetes/docker-kubernetes.html) | 1 |
| Learn | [`Docker-Kubernetes/learn/`](Docker-Kubernetes/learn/) | 18 |
| Cheat sheets | [`Docker-Kubernetes/cheatsheets/`](Docker-Kubernetes/cheatsheets/) | 3 |

Docker, Kubernetes (architecture, workloads, scheduling, autoscaling, networking, storage, security, observability, GPUs, debugging broken pods, operators and custom resources), and DevOps/MLOps (`DevOps/`, including infrastructure as code). The learn pages have a suggested reading order with Previous / Next links.

### Graph Machine Learning

| Track | Path | Pages |
|-------|------|------:|
| Hub | [`Graph ML/graph-ml.html`](Graph%20ML/graph-ml.html) | 1 |
| Learn | [`Graph ML/learn/`](Graph%20ML/learn/) | 13 |
| Formulas | [`Graph ML/formulas/`](Graph%20ML/formulas/) | 1 |
| Papers hub | [`Graph ML/research/`](Graph%20ML/research/) | 1 |

### Interactive Labs

| Lab | Path |
|-----|------|
| Hub | [`Interactive Labs/index.html`](Interactive%20Labs/index.html) |
| Self-attention, step by step | [`Interactive Labs/attention.html`](Interactive%20Labs/attention.html) |
| LLM sampling (temperature, top-k, top-p, min-p) | [`Interactive Labs/sampling.html`](Interactive%20Labs/sampling.html) |
| CPU scheduling (FCFS, SJF, SRTF, RR, Priority) | [`Interactive Labs/cpu-scheduling.html`](Interactive%20Labs/cpu-scheduling.html) |
| Page replacement (FIFO, LRU, OPT) | [`Interactive Labs/page-replacement.html`](Interactive%20Labs/page-replacement.html) |
| Load balancing (p99 latency with a slow server) | [`Interactive Labs/load-balancing.html`](Interactive%20Labs/load-balancing.html) |
| Subnet calculator | [`Interactive Labs/subnet-calculator.html`](Interactive%20Labs/subnet-calculator.html) |

Labs are plain HTML and JavaScript with no libraries. They share `assets/labs.css`, work on phones, and follow the site theme. Related guides link to them.

Page counts exclude each track's own hub page (for example `learn/docker-kubernetes-learn.html`).

## Project structure

```
Engineering-Knowledge-Base/
├── index.html
├── .github/workflows/site-checks.yml   # CI: fails a PR if generated files are stale, a link is broken, or a diagram is invalid
├── 404.html               # Custom not-found page (root-relative links; served by the host for missing URLs)
├── styles.css               # Whole site design, light and dark themes
├── assets/
│   ├── logo.svg
│   ├── og-image.png         # Social share image (1200x630)
│   ├── labs.css             # Shared styles for the interactive labs
│   ├── site.js              # Theme toggle, mobile menu, path normalization for local browsing, code copy buttons, wide-math fix, section links, back-to-top, reading time, progress bar, skip link, TOC highlight
│   ├── search.js            # Fuzzy site search
│   ├── search-index.js      # Generated index (commit with content changes)
│   └── search-index.json
├── sitemap.xml             # Generated with the search index (https://engineering.msaqlain.com)
├── robots.txt              # Allows search engines and AI crawlers, points at sitemap.xml
├── llms.txt                # Site map for AI assistants (https://llmstxt.org), generated
├── scripts/
│   ├── apply-layout.py         # Shared head tags (theme, canonical, Open Graph, JSON-LD), top bar, and footer on every page
│   ├── diagrams.py             # Inline SVG architecture diagrams, with layout checks (text fits, no overlaps, arrows end on boxes)
│   ├── build-search-index.py   # Search index, sitemap.xml (with lastmod), robots.txt, and llms.txt builder (Python 3, no dependencies)
│   ├── build-search-index.ps1  # Wrapper that calls the Python builder
│   ├── check-links.py          # Internal link and #anchor checker; also fails if a learn page is missing from its learn hub
│   ├── check-pages.py          # Page basics: one title and h1, meta description, viewport, unique ids, no em dashes, balanced tags
│   └── update-prev-next.py     # Previous / Next links along a track's reading order
├── Interactive Labs/       # Lab hub and one HTML file per lab
└── AI Engineer/
    ├── ai-engineering.html
    ├── index.html           # Redirects to subject hub
    ├── learn/
    └── research/
```

## Tech stack

| Layer | Choice |
|-------|--------|
| Markup | HTML5 |
| Styling | CSS (`styles.css`, `assets/labs.css`), light and dark themes |
| Search and labs | Vanilla JS (no frameworks, no bundler) |
| Hosting | Static file server |

## Search index

After adding or renaming pages:

```bash
python3 scripts/build-search-index.py
```

(`powershell -File scripts/build-search-index.ps1` still works and calls the same script.) Commit the updated `assets/search-index.js`, `assets/search-index.json`, `sitemap.xml`, `robots.txt`, and `llms.txt` with your changes. Never edit these files by hand.

## Shared layout and diagrams

The top bar, footer, theme script, and SEO tags (canonical URL, Open Graph, Twitter card, JSON-LD) are written into every page by one script. After adding a page or changing the nav:

```bash
python3 scripts/apply-layout.py           # rewrites the marked blocks; safe to run again
python3 scripts/apply-layout.py --check   # exits 1 if any page is out of date
```

Architecture diagrams are defined in `scripts/diagrams.py` and written into pages as inline SVG (never as images in a README). The script checks each diagram before writing it: text must fit its box, boxes must not overlap, arrows must start and end on box edges, and labels must not sit on lines or boxes.

```bash
python3 scripts/diagrams.py               # validate and write all diagrams
python3 scripts/diagrams.py --check       # exits 1 on a layout problem or a stale page
```

## Previous / Next links

When you add a page to a track's suggested reading order, add it to the list in `scripts/update-prev-next.py` too, then run:

```bash
python3 scripts/update-prev-next.py
```

The script rewrites the block between `<!-- prev-next:start -->` and `<!-- prev-next:end -->` on every page in the order, so running it again is safe.

## Checking links and pages

```bash
python3 scripts/check-links.py            # whole site; exits 1 if any internal link or #anchor is broken,
                                          # or if a learn page is not linked from its track's learn hub
python3 scripts/check-links.py AI\ Engineer   # one folder
```

```bash
python3 scripts/check-pages.py            # every page: title, description, viewport, one <h1>, unique ids, canonical link,
                                          # titles and descriptions unique across the site,
                                          # no em dashes, and balanced tags (a raw "<" in math breaks a page)
```

All of these checks, plus `update-prev-next.py --check`, `apply-layout.py --check`, `diagrams.py --check`, and a stale generated-files check, run automatically on every pull request (`.github/workflows/site-checks.yml`).

## Contributing

1. Fork the repository.
2. Create a branch (for example `add-eval-guide`).
3. Match existing page structure: breadcrumbs and relative paths. Run `scripts/apply-layout.py` for the top bar and footer.
4. Regenerate the search index if pages changed, and run the checks.
5. Open a pull request against `main`.

See [CONTRIBUTING.md](CONTRIBUTING.md) for path conventions and file naming.

## Deployment

Deploy the repository root to GitHub Pages, Cloudflare Pages, Netlify, or similar. No build step is required.

Production site: [https://engineering.msaqlain.com](https://engineering.msaqlain.com)

## License

No `LICENSE` file is in the repository yet. Contact the maintainer on GitHub for reuse questions.

## Acknowledgments

Maintained by [@saqlain2204](https://github.com/saqlain2204). External sources cited on learn pages belong to their respective authors.
