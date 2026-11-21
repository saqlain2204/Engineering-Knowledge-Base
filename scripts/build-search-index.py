#!/usr/bin/env python3
"""Regenerate assets/search-index.json and assets/search-index.js from all HTML pages.

Cross-platform port of scripts/build-search-index.ps1 (Python 3.8+, standard library only).
Run from anywhere:  python3 scripts/build-search-index.py
"""
import html as htmllib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TITLE_SUFFIXES = [
    r"\s*\|\s*Interview Prep\s*$",
    r"\s*\|\s*AI Engineering\s*$",
    r"\s*\|\s*Docker & Kubernetes\s*$",
    r"\s*\|\s*Docker &amp; Kubernetes\s*$",
    r"\s*\|\s*Graph Machine Learning\s*$",
    r"\s*\|\s*CS Fundamentals\s*$",
    r"\s*-\s*AI Engineering\s*$",
]

HUB_PATTERNS = [
    r"index\.html$", r"ai-engineering\.html$", r"docker-kubernetes\.html$", r"graph-ml\.html$",
    r"cs-fundamentals\.html$", r"research-hub\.html$", r"papers-hub\.html$",
    r"ai-engineering-interview\.html$", r"docker-kubernetes-interview\.html$",
    r"graph-ml-interview\.html$", r"docker-kubernetes-cheatsheets\.html$", r"graph-ml-formulas\.html$",
]

# Extra search keywords for pages whose path matches a pattern.
KEYWORDS = [
    (r"reinforcement", ["RL", "reinforcement learning", "PPO", "DPO", "GRPO", "policy gradient", "reward"]),
    (r"-rag\.html$", ["retrieval", "augmented generation", "RAG"]),
    (r"transformer", ["attention", "transformer", "self-attention"]),
    (r"inference-optimization", ["KV cache", "PagedAttention", "vLLM", "continuous batching",
                                 "speculative decoding", "TTFT", "prefill", "decode", "LLM serving"]),
    (r"os-processes", ["operating system", "OS", "CPU scheduling", "round robin", "SJF", "FCFS",
                       "fork", "context switch", "CFS", "EEVDF"]),
    (r"os-virtual-memory", ["operating system", "OS", "paging", "page table", "TLB", "page fault",
                            "LRU", "page replacement", "OOM"]),
    (r"dbms-transactions", ["DBMS", "database", "ACID", "isolation level", "MVCC", "deadlock",
                            "PostgreSQL", "MySQL", "serializable", "WAL"]),
    (r"cn-tcp", ["computer networks", "CN", "TCP", "handshake", "congestion control", "QUIC",
                 "HTTP/3", "TLS", "TIME_WAIT"]),
    (r"os-concurrency", ["operating system", "OS", "race condition", "mutex", "semaphore", "deadlock",
                         "spinlock", "condition variable", "producer consumer", "Banker's algorithm",
                         "dining philosophers", "priority inversion", "critical section"]),
    (r"dbms-indexing", ["DBMS", "database", "index", "B-tree", "B+ tree", "EXPLAIN", "query plan",
                        "composite index", "covering index", "LSM", "PostgreSQL", "slow query"]),
    (r"cn-dns-http", ["computer networks", "CN", "DNS", "HTTP", "TTL", "CNAME", "status codes",
                      "cookies", "ETag", "caching", "CDN", "idempotency", "ndots", "resolver"]),
    (r"scenario-slow-api", ["scenario", "latency", "p99", "percentile", "Little's law", "connection pool",
                            "RED method", "USE method", "vmstat", "postmortem", "retry storm", "debugging"]),
    (r"gpu-scheduling", ["GPU", "MIG", "DRA", "device plugin", "NVIDIA", "Kueue", "time-slicing"]),
    (r"-fine-tuning\.html$", ["fine-tuning", "LoRA", "QLoRA", "PEFT", "SFT", "adapters", "instruction tuning"]),
    (r"classical-ml", ["machine learning", "ML", "linear regression", "logistic regression", "gradient descent",
                       "overfitting", "cross-validation", "precision", "recall", "F1", "ROC", "AUC",
                       "confusion matrix", "data leakage", "scikit-learn", "train test split"]),
    (r"quantization", ["quantization", "INT8", "INT4", "FP8", "BF16", "GPTQ", "AWQ", "SmoothQuant",
                       "NF4", "GGUF", "llama.cpp", "bitsandbytes", "W4A16", "W8A8"]),
    (r"devops-cicd-mlops", ["CI/CD", "CI", "CD", "DevOps", "MLOps", "GitHub Actions", "GitOps", "Argo CD",
                            "canary", "blue-green", "rollback", "model registry", "MLflow", "drift", "PSI",
                            "KServe", "pipeline"]),
]


def strip_html_text(html: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", html)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", " and ")
    text = re.sub(r"&[^;\s]+;", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def page_entry(path: Path) -> dict:
    rel = path.relative_to(ROOT).as_posix()
    html = path.read_text(encoding="utf-8")

    m = re.search(r"<title>([^<]+)</title>", html)
    title = m.group(1).strip() if m else path.stem
    for suffix in TITLE_SUFFIXES:
        title = re.sub(suffix, "", title)
    title = htmllib.unescape(title)

    # Short summary shown under each search hit: the page's meta description,
    # else the first paragraph after the <h1> (tags stripped). The old pattern
    # skipped any paragraph containing a link and could pick a random line
    # from the page body instead.
    m = re.search(r'<meta name="description" content="([^"]*)"', html)
    if not m:
        m = re.search(r"</h1>\s*<p[^>]*>([\s\S]*?)</p>", html)
    desc = htmllib.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()) if m else ""
    if len(desc) > 220:
        desc = desc[:220].rsplit(" ", 1)[0].rstrip(",;:") + "..."

    headings = [htmllib.unescape(re.sub(r"^\d+\.\s*", "", h.strip())) for h in re.findall(r"<h2[^>]*>([^<]+)</h2>", html)]
    details = [htmllib.unescape(s.strip()) for s in re.findall(r"<summary>([^<]+)</summary>", html)]

    m = re.search(r"<main[\s\S]*?</main>", html)
    main_text = strip_html_text(m.group(0)) if m else ""

    if "/learn/" in rel:
        page_type = "learn"
    elif "/interview/" in rel:
        page_type = "interview"
    elif "/research/" in rel:
        page_type = "research"
    elif any(re.search(p, rel) for p in HUB_PATTERNS):
        page_type = "hub"
    else:
        page_type = "page"

    joined = " ".join([title, desc] + headings + details + [main_text])
    keywords = []
    if 'class="badge-interview"' in html:
        keywords.append("interview")
    for pattern, words in KEYWORDS:
        if re.search(pattern, rel):
            keywords.extend(words)

    return {
        "path": rel,
        "title": title,
        "type": page_type,
        "description": desc,
        "headings": headings[:50],
        "keywords": keywords,
        "text": joined[:4000],
    }


def main() -> None:
    pages = []
    for p in sorted(ROOT.rglob("*.html")):
        if ".git" in p.parts:
            continue
        if p.name == "404.html":
            continue  # error page, not content
        if 'http-equiv="refresh"' in p.read_text(encoding="utf-8"):
            continue  # redirect stubs (e.g. AI Engineer/index.html) would only duplicate hub results
        pages.append(page_entry(p))
    data = json.dumps({"pages": pages}, ensure_ascii=False, indent=2)
    (ROOT / "assets" / "search-index.json").write_text(data + "\n", encoding="utf-8")
    (ROOT / "assets" / "search-index.js").write_text(
        "// Auto-generated by scripts/build-search-index.py\nwindow.__SEARCH_INDEX__ = " + data + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(pages)} pages to assets/search-index.json and assets/search-index.js")


if __name__ == "__main__":
    main()
