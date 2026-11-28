#!/usr/bin/env python3
"""Regenerate assets/search-index.json, assets/search-index.js, sitemap.xml, robots.txt and llms.txt.

Cross-platform port of scripts/build-search-index.ps1 (Python 3.8+, standard library only).
Run from anywhere:  python3 scripts/build-search-index.py
"""
import html as htmllib
import json
import re
import subprocess
from datetime import date
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent

TITLE_SUFFIXES = [
    r"\s*\|\s*AI Engineering\s*$",
    r"\s*\|\s*Docker & Kubernetes\s*$",
    r"\s*\|\s*Docker &amp; Kubernetes\s*$",
    r"\s*\|\s*Graph Machine Learning\s*$",
    r"\s*\|\s*CS Fundamentals\s*$",
    r"\s*-\s*AI Engineering\s*$",
    r"\s*\|\s*Interactive Labs\s*$",
    r"\s*\|\s*Engineering Knowledge Base\s*$",
]

HUB_PATTERNS = [
    r"index\.html$", r"ai-engineering\.html$", r"docker-kubernetes\.html$", r"graph-ml\.html$",
    r"cs-fundamentals\.html$", r"research-hub\.html$", r"papers-hub\.html$",
    r"docker-kubernetes-cheatsheets\.html$", r"graph-ml-formulas\.html$",
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
    (r"os-cpu-caches", ["operating system", "OS", "CPU cache", "cache line", "L1", "L2", "L3",
                        "memory hierarchy", "locality", "set associative", "AMAT", "cache miss",
                        "false sharing", "MESI", "cache coherence", "NUMA", "write-back"]),
    (r"containers-under-the-hood", ["container internals", "namespaces", "cgroups", "cgroup v2", "unshare",
                                    "nsenter", "overlayfs", "whiteout", "OCI", "runc", "containerd",
                                    "PID 1", "SIGTERM", "veth", "seccomp", "capabilities", "image layers"]),
    (r"scenario-pod-oomkilled", ["scenario", "OOMKilled", "OOM", "exit code 137", "memory leak",
                                 "CrashLoopBackOff", "evicted", "working set", "memory limit",
                                 "requests and limits", "QoS", "oom_score_adj", "tracemalloc",
                                 "GOMEMLIMIT", "MaxRAMPercentage", "debugging"]),
    (r"reasoning-test-time-compute", ["reasoning models", "test-time compute", "inference-time compute",
                                      "thinking tokens", "chain of thought", "CoT", "self-consistency",
                                      "majority voting", "best-of-N", "verifier", "pass@k", "PRM",
                                      "process reward model", "GRPO", "RLVR", "DeepSeek-R1",
                                      "budget forcing", "overthinking"]),
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
    (r"os-io-models", ["operating system", "OS", "event loop", "epoll", "select", "poll", "kqueue",
                       "non-blocking", "async", "await", "asyncio", "C10K", "thread pool", "io_uring",
                       "edge-triggered", "level-triggered", "backpressure", "Node.js"]),
    (r"cn-load-balancing", ["computer networks", "CN", "load balancer", "reverse proxy", "nginx", "HAProxy",
                            "Envoy", "Layer 4", "Layer 7", "L4", "L7", "round robin", "least connections",
                            "power of two choices", "health check", "sticky sessions", "X-Forwarded-For",
                            "gRPC", "anycast", "GeoDNS", "ALB", "NLB"]),
    (r"scenario-database-lock-waits", ["scenario", "database", "PostgreSQL", "MySQL", "lock wait", "deadlock",
                                       "lock_timeout", "idle in transaction", "pg_stat_activity",
                                       "pg_blocking_pids", "migration", "ALTER TABLE", "40P01", "debugging"]),
    (r"ai-engineering-agents\.html$", ["agents", "AI agent", "tool use", "function calling", "tool calling",
                                        "ReAct", "MCP", "Model Context Protocol", "prompt injection",
                                        "pass^k", "agent evaluation", "multi-agent", "plan-and-execute"]),
    (r"dbms-joins-execution", ["DBMS", "database", "SQL join", "inner join", "left join", "hash join",
                               "nested loop join", "merge join", "EXPLAIN", "cross join", "anti-join",
                               "NULL", "query execution"]),
    (r"os-system-calls", ["operating system", "OS", "system call", "syscall", "kernel", "user space",
                          "strace", "vDSO", "getpid", "seccomp", "errno", "file descriptor"]),
    (r"cn-quic-http3", ["computer networks", "CN", "QUIC", "HTTP/3", "HTTP3", "UDP", "head-of-line blocking",
                        "HOL", "0-RTT", "connection ID", "QPACK", "Alt-Svc", "stream"]),
    (r"devops-infrastructure-as-code", ["DevOps", "IaC", "infrastructure as code", "Terraform", "OpenTofu",
                                        "Pulumi", "Ansible", "desired state", "drift", "state file",
                                        "terraform plan", "reconcile"]),
    (r"scenario-retry-storm", ["scenario", "retry storm", "thundering herd", "backoff", "jitter",
                               "retry budget", "circuit breaker", "load shedding", "timeout",
                               "abandoned work", "idempotency", "amplification"]),
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
    elif rel.startswith("Interactive Labs/") and not rel.endswith("index.html"):
        page_type = "lab"
    elif "/research/" in rel:
        page_type = "research"
    elif any(re.search(p, rel) for p in HUB_PATTERNS):
        page_type = "hub"
    else:
        page_type = "page"

    joined = " ".join([title, desc] + headings + details + [main_text])
    keywords = []
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


SITE_URL = "https://engineering.msaqlain.com"


def git_lastmod(rel: str) -> str:
    """Last change date (YYYY-MM-DD) of a page.

    A page with uncommitted edits gets today's date. Otherwise the date of the
    last commit that touched it. CI ignores <lastmod> lines when it checks that
    generated files are fresh, because shallow clones see other dates.
    """
    try:
        dirty = subprocess.run(["git", "status", "--porcelain", "--", rel], cwd=ROOT,
                               capture_output=True, text=True, check=True).stdout.strip()
        if dirty:
            return date.today().isoformat()
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", rel], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout.strip()
        return out or date.today().isoformat()
    except (OSError, subprocess.CalledProcessError):
        return date.today().isoformat()


def page_url(rel: str) -> str:
    if rel == "index.html":
        return SITE_URL + "/"
    return SITE_URL + "/" + quote(rel, safe="/")


# Crawlers named explicitly so the policy is clear. Everything is allowed.
CRAWLERS = [
    "Googlebot", "Bingbot", "DuckDuckBot", "Applebot", "Google-Extended", "Applebot-Extended",
    "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User",
    "PerplexityBot", "Perplexity-User", "CCBot", "Meta-ExternalAgent", "Amazonbot", "cohere-ai",
    "MistralAI-User", "YouBot",
]


def write_sitemap_and_robots(pages: list) -> None:
    """Write sitemap.xml and robots.txt for the public site.

    Paths match the generated search index (redirect stubs and 404 are omitted).
    index.html is listed as the site root. Spaces in folder names are encoded.
    """
    body = "\n".join(
        f"  <url>\n    <loc>{page_url(page['path'])}</loc>\n    <lastmod>{git_lastmod(page['path'])}</lastmod>\n  </url>"
        for page in pages
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + body
        + "\n</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")
    robots = "# Search engines and AI assistants are welcome to read and cite this site.\n\n"
    robots += "".join(f"User-agent: {bot}\n" for bot in CRAWLERS)
    robots += "Allow: /\n\nUser-agent: *\nAllow: /\n\n"
    robots += f"Sitemap: {SITE_URL}/sitemap.xml\n"
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")


LLMS_SECTIONS = [
    ("Start here", lambda r: r in ("index.html", "Interactive Labs/index.html") or r.endswith(("ai-engineering.html", "cs-fundamentals.html", "docker-kubernetes.html", "graph-ml.html"))),
    ("Interactive labs", lambda r: r.startswith("Interactive Labs/")),
    ("AI Engineering", lambda r: r.startswith("AI Engineer/") and "/research/" not in r),
    ("Research and books", lambda r: "/research/" in r),
    ("CS Fundamentals", lambda r: r.startswith("CS-Fundamentals/")),
    ("Docker and Kubernetes", lambda r: r.startswith("Docker-Kubernetes/")),
    ("Graph Machine Learning", lambda r: r.startswith("Graph ML/")),
    ("Other", lambda r: True),
]


def write_llms_txt(pages: list) -> None:
    """Write llms.txt (https://llmstxt.org): a short map of the site for AI tools."""
    groups = {name: [] for name, _ in LLMS_SECTIONS}
    for page in pages:
        for name, match in LLMS_SECTIONS:
            if match(page["path"]):
                groups[name].append(page)
                break
    out = [
        "# Engineering Knowledge Base",
        "",
        "> Free, beginner-friendly guides to AI engineering, computer science fundamentals, "
        "Docker and Kubernetes, and graph machine learning. Every page explains ideas in plain "
        "words, works examples by hand, and links to in-browser interactive labs. "
        "Written and maintained by Mohammed Saqlain (https://github.com/saqlain2204).",
        "",
        "Content is plain HTML with no paywall or login. Citations with a link to the page are welcome. "
        f"Full page list: {SITE_URL}/sitemap.xml",
        "",
    ]
    for name, _ in LLMS_SECTIONS:
        items = groups[name]
        if not items:
            continue
        out.append(f"## {name}")
        out.append("")
        for page in items:
            desc = page["description"].replace("\n", " ").strip()
            out.append(f"- [{page['title']}]({page_url(page['path'])})" + (f": {desc}" if desc else ""))
        out.append("")
    (ROOT / "llms.txt").write_text("\n".join(out), encoding="utf-8")


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
    write_sitemap_and_robots(pages)
    write_llms_txt(pages)
    print(f"Wrote {len(pages)} pages to assets/search-index.json and assets/search-index.js")
    print(f"Wrote sitemap.xml, robots.txt and llms.txt ({len(pages)} URLs)")


if __name__ == "__main__":
    main()
