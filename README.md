# Engineering Knowledge Base

Structured notes, revision guides, and interview preparation for engineering disciplines. Built as a fast, static site with no framework and no build step.

**Live site:** [https://engineering.msaqlain.com](https://engineering.msaqlain.com)

**Repository:** [github.com/saqlain2204/Engineering-Knowledge-Base](https://github.com/saqlain2204/Engineering-Knowledge-Base)

**Maintainer:** [@saqlain2204](https://github.com/saqlain2204)

---

## Overview

Engineering Knowledge Base is an open learning resource for engineers preparing for technical roles or deepening domain expertise. Content is organized by **subject**, then split into two parallel tracks:

| Track | Purpose |
|-------|---------|
| **Learn** | Deep reference notes: concepts, pipelines, tradeoffs, and code snippets |
| **Interview Prep** | Expandable Q&A (`<details>`) for revision and mock interviews |

Each learn topic is paired with a matching interview page where applicable. The site is plain HTML and CSS, designed to be readable, forkable, and easy to contribute to without tooling overhead.

---

## Current subjects

### AI Engineering

Hub: [`AI Engineer/ai-engineering.html`](AI%20Engineer/ai-engineering.html)

Covers the full AI engineering stack from foundations through production.

#### Learn topics (24 pages)

| Section | Topics |
|---------|--------|
| **Foundations and Architecture** | Foundations, Transformers, Tokenization, LLMs, SLMs |
| **Training Pipeline** | Pretraining, Distributed Training, Fine-Tuning, Post-Training |
| **Prompting and Retrieval** | Prompt Engineering, Embeddings, Vector Databases, RAG |
| **Inference, Deployment, Operations** | Inference Optimization, Deployment, LLMOps and Monitoring, Evaluation |
| **Agents and Protocols** | Agents, MCP |
| **Frameworks** | LangChain, LangGraph, Langfuse |
| **Safety and System Design** | Safety, System Design |

#### Interview Prep (21 topic pages + hub)

Mirrors the core AI Engineering curriculum (Foundations through System Design). Framework-specific interview pages are not included yet; framework content is learn-only.

Hub: [`AI Engineer/interview/ai-engineering-interview.html`](AI%20Engineer/interview/ai-engineering-interview.html)

---

## Site architecture

```
Home (index.html)
└── Subject hub (e.g. AI Engineer/ai-engineering.html)
    ├── Learn track (AI Engineer/learn/*.html)
    └── Interview track (AI Engineer/interview/*.html)
```

**Navigation flow**

1. **Home** lists all subjects.
2. **Subject hub** shows Learn and Interview Prep entry points plus topic lists.
3. **Topic page** is a self-contained article with breadcrumbs, body content, and links back to the hub.

**URL mapping (production)**

| Path | Page |
|------|------|
| `/` | Home |
| `/AI Engineer/ai-engineering.html` | AI Engineering hub |
| `/AI Engineer/learn/ai-engineering-rag.html` | Example learn page |
| `/AI Engineer/interview/ai-engineering-interview-rag.html` | Example interview page |

---

## Repository structure

```
Engineering-Knowledge-Base/
├── index.html              # Site home, subjects list, contribution guidelines
├── styles.css              # Global dark-theme stylesheet (shared by all pages)
├── assets/
│   └── logo.svg            # Site favicon and header logo
├── AI Engineer/
│   ├── ai-engineering.html # Subject hub
│   ├── learn/              # Learning notes (24 HTML files)
│   └── interview/          # Interview Q&A (23 HTML files)
└── README.md
```

### Design principles

- **Modular subjects** — each discipline lives in its own folder (`AI Engineer/`, future subjects follow the same pattern).
- **Shared root assets** — `index.html`, `styles.css`, and `assets/` stay at the repo root.
- **Relative links only** — pages work locally and on any static host without a base URL config.
- **No build step** — edit HTML, open in a browser, commit. Suitable for GitHub Pages, Cloudflare Pages, Netlify, S3, or any static file server.
- **External references for diagrams** — learn pages use compact `refer-link` citations instead of bundled images.

---

## Tech stack

| Layer | Choice |
|-------|--------|
| Markup | Semantic HTML5 |
| Styling | Single CSS file (`styles.css`), CSS custom properties |
| JavaScript | None (by design) |
| Fonts | System font stack |
| Theme | Dark mode, responsive layout |

### Page types and CSS classes

| Class / pattern | Used on |
|-----------------|---------|
| Default `body` | Home, subject hubs |
| `learn-page` + `article` | Learn topic pages |
| `badge-interview` | Interview section headers |
| `refer-link` | External diagram/source citations on learn pages |
| `callout` | Highlighted tips on learn pages |
| `hub-track-learn` / `hub-track-interview` | Subject hub track cards |
| `<details>` / `<summary>` | Interview Q&A accordions |

---

## Local development

No install or compile step is required.

### Option 1: Open directly

Open `index.html` in a browser. Relative links resolve from the file path.

### Option 2: Local static server (recommended)

Serving over HTTP avoids quirks with some browsers and `file://` paths.

**Python**

```bash
python -m http.server 8080
```

Then visit [http://localhost:8080](http://localhost:8080).

**Node.js (npx)**

```bash
npx serve .
```

**VS Code / Cursor**

Use a “Live Server” or “Simple Browser” extension pointed at the repo root.

### Verify your changes

1. Check breadcrumb links (Home → Subject → Topic).
2. Confirm `styles.css` loads (page should use the dark theme).
3. Click footer and cross-links (Learn ↔ Interview where paired).
4. Validate HTML if you use an editor extension (optional).

---

## Deployment

The production site is hosted at **https://engineering.msaqlain.com**.

Because the project is static, deployment is a file upload or git push to any static hosting provider:

- **GitHub Pages** — publish from `main`, root directory
- **Cloudflare Pages** — connect repo, no build command, output directory `/`
- **Netlify** — same as above
- **Custom domain** — point DNS to your host; no server-side config needed

There is no environment-specific build. The same files served locally are what go to production.

---

## Contributing

Contributions are welcome: new subjects, learn pages, interview questions, fixes, and clearer explanations.

### Quick start

1. Fork [Engineering-Knowledge-Base](https://github.com/saqlain2204/Engineering-Knowledge-Base).
2. Create a branch (e.g. `add-backend-engineering-foundations`).
3. Make changes following the conventions below.
4. Open a pull request against `main` with a short description of what changed and why.

### What to contribute

- **New subjects** — folder + hub page + `learn/` and `interview/` subfolders
- **Learn pages** — technical depth, accurate terminology, short code examples where useful
- **Interview Q&A** — realistic questions with strong answers in `<details>` blocks
- **Fixes** — typos, broken links, outdated API names, factual corrections

### File naming

| Type | Pattern | Example |
|------|---------|---------|
| Subject hub | `{subject}.html` in subject folder | `ai-engineering.html` |
| Learn page | `ai-engineering-{topic}.html` | `ai-engineering-rag.html` |
| Interview page | `ai-engineering-interview-{topic}.html` | `ai-engineering-interview-rag.html` |
| Framework learn | `ai-engineering-frameworks-{name}.html` | `ai-engineering-frameworks-langchain.html` |

### Authoring conventions

**Learn page template (paths from `AI Engineer/learn/`)**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Topic Name | AI Engineering</title>
  <link rel="stylesheet" href="../../styles.css">
</head>
<body class="learn-page">
<header>
  <nav aria-label="Breadcrumb">
    <p><a href="../../index.html">Home</a> &rsaquo; <a href="../ai-engineering.html">AI Engineering</a> &rsaquo; Topic Name</p>
  </nav>
  <h1>Page Title</h1>
  <p>One-line summary.</p>
</header>
<main class="article">
  <section>
    <h2>Section</h2>
    <p>Content...</p>
    <p class="refer-link"><small>Refer: <a href="https://..." rel="noopener noreferrer">Source</a></small></p>
  </section>
  <nav class="page-footer-nav">
    <p><a class="interview-link" href="../interview/ai-engineering-interview-topic.html">Interview questions on Topic</a></p>
    <p><a href="../ai-engineering.html">Back to AI Engineering</a></p>
  </nav>
</main>
<footer>
  <p><small><a href="../ai-engineering.html">Back to AI Engineering</a> &middot; <a href="../../index.html">Home</a></small></p>
</footer>
</body>
</html>
```

**Interview page pattern**

- Use `<details><summary>Question</summary><div><p>Answer</p></div></details>` for each Q&A.
- Link to the corresponding learn page in the header.
- Stylesheet path: `../../styles.css` from `AI Engineer/interview/`.

**Relative path cheat sheet**

| From | To `styles.css` | To `index.html` |
|------|-----------------|-----------------|
| Repo root | `styles.css` | `index.html` |
| `AI Engineer/` | `../styles.css` | `../index.html` |
| `AI Engineer/learn/` or `interview/` | `../../styles.css` | `../../index.html` |

### Pull request guidelines

- Keep PRs focused (one subject or topic area when possible).
- Prefer accurate, plain language over marketing tone.
- Cite authoritative sources for non-obvious claims.
- Do not embed large images without discussion; use `refer-link` citations.
- Update the subject hub (`ai-engineering.html`) when adding new topic pages.

### Questions

Open a [GitHub issue](https://github.com/saqlain2204/Engineering-Knowledge-Base/issues) for bugs, content requests, or structural suggestions.

---

## Roadmap (informal)

Planned directions for the project:

- Additional engineering subjects (e.g. Backend, System Design, DevOps)
- Interview pages for Frameworks (LangChain, LangGraph, Langfuse)
- More cross-linking between related learn topics
- Community-contributed topics and corrections

---

## License

License terms for contributions will be documented in a `LICENSE` file. Until then, contact the maintainer via GitHub for usage questions.

---

## Acknowledgments

Built and maintained by [@saqlain2204](https://github.com/saqlain2204). External references and citations on learn pages belong to their respective authors and projects.
