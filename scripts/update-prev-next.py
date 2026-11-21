#!/usr/bin/env python3
"""Write "Previous / Next" links on learn pages that follow a reading order.

Each track lists its pages in reading order (the same order as the
"Suggested reading order" list on the track's learn hub). The script puts a
<nav class="prev-next"> block between the markers
    <!-- prev-next:start -->  ...  <!-- prev-next:end -->
or, the first time, right before the page's page-footer-nav block
(<nav class="page-footer-nav"> or <div class="page-footer-nav">).

Run it after adding a page to a track, then run scripts/check-links.py:
  python3 scripts/update-prev-next.py           # write the blocks
  python3 scripts/update-prev-next.py --check   # CI: fail if anything is stale,
                                                # or if a hub's reading order
                                                # does not match TRACKS
"""
import os
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent

# track folder -> (learn hub file inside that folder, pages in reading order)
TRACKS = {
    "CS-Fundamentals/learn": ("cs-fundamentals-learn.html", [
        "Operating-Systems/os-processes-threads-scheduling.html",
        "Operating-Systems/os-virtual-memory-paging.html",
        "Operating-Systems/os-file-systems-io.html",
        "Operating-Systems/os-concurrency-synchronization-deadlocks.html",
        "Databases/dbms-normalization-schema-design.html",
        "Databases/dbms-transactions-isolation-mvcc.html",
        "Databases/dbms-indexing-btrees-query-plans.html",
        "Databases/dbms-replication-sharding-cap.html",
        "Computer-Networks/cn-ip-addressing-subnetting-routing.html",
        "Computer-Networks/cn-tcp-deep-dive.html",
        "Computer-Networks/cn-dns-http.html",
        "Computer-Networks/cn-tls-https-certificates.html",
        "Scenarios/scenario-slow-api-debugging.html",
        "Scenarios/scenario-service-cannot-reach-database.html",
        "Scenarios/scenario-errors-during-deploys.html",
    ]),
    "Docker-Kubernetes/learn": ("docker-kubernetes-learn.html", [
        "Docker/docker-fundamentals.html",
        "Docker/docker-compose.html",
        "Docker/docker-advanced.html",
        "Kubernetes/kubernetes-architecture.html",
        "Kubernetes/kubernetes-workloads.html",
        "Kubernetes/kubernetes-autoscaling-probes-rollouts.html",
        "Kubernetes/kubernetes-networking.html",
        "Kubernetes/kubernetes-storage.html",
        "Kubernetes/kubernetes-config-security.html",
        "Kubernetes/kubernetes-helm-observability.html",
        "Kubernetes/kubernetes-gpu-scheduling.html",
        "DevOps/devops-cicd-mlops.html",
    ]),
}

START, END = "<!-- prev-next:start -->", "<!-- prev-next:end -->"
BLOCK_RE = re.compile(r"[ \t]*" + re.escape(START) + r".*?" + re.escape(END) + r"\n?", re.S)
H1_RE = re.compile(r"<h1>(.*?)</h1>", re.S)
FOOTER_RE = re.compile(r'^([ \t]*)<(?:nav|div) class="page-footer-nav">', re.M)
PATH_RE = re.compile(r'<ol class="learning-path">(.*?)</ol>', re.S)
HREF_RE = re.compile(r'<li><a href="([^"]+)"')


def title_of(path: Path) -> str:
    m = H1_RE.search(path.read_text(encoding="utf-8"))
    return m.group(1).strip() if m else path.stem


def link(from_page: Path, to_page: Path) -> str:
    return os.path.relpath(to_page, from_page.parent).replace(os.sep, "/")


def block_for(pages, i, indent):
    page, total = pages[i], len(pages)
    lines = [f"{indent}{START}", f'{indent}<nav class="prev-next" aria-label="Reading order">']
    if i > 0:
        prev = pages[i - 1]
        lines.append(
            f'{indent}  <a class="prev-next-prev" href="{link(page, prev)}" rel="prev">'
            f'<span class="prev-next-label">&larr; Previous</span>'
            f'<span class="prev-next-title">{title_of(prev)}</span></a>'
        )
    if i < total - 1:
        nxt = pages[i + 1]
        lines.append(
            f'{indent}  <a class="prev-next-next" href="{link(page, nxt)}" rel="next">'
            f'<span class="prev-next-label">Next &rarr;</span>'
            f'<span class="prev-next-title">{title_of(nxt)}</span></a>'
        )
    lines.append(f'{indent}  <p class="prev-next-step">Page {i + 1} of {total} in the suggested reading order</p>')
    lines.append(f"{indent}</nav>")
    lines.append(f"{indent}{END}")
    return "\n".join(lines) + "\n"


def main(check: bool) -> int:
    problems, changed = [], 0
    for base, (hub, order) in TRACKS.items():
        pages = [root / base / p for p in order]
        missing = [p for p in pages if not p.exists()]
        if missing:
            problems += [f"{p.relative_to(root)}: listed in TRACKS but missing" for p in missing]
            continue

        # the hub's "Suggested reading order" must list the same pages, in order
        hub_text = (root / base / hub).read_text(encoding="utf-8")
        m = PATH_RE.search(hub_text)
        hub_order = HREF_RE.findall(m.group(1)) if m else []
        if hub_order != order:
            problems.append(f"{base}/{hub}: 'Suggested reading order' does not match TRACKS in this script")

        for i, page in enumerate(pages):
            text = page.read_text(encoding="utf-8")
            if START in text:
                mb = BLOCK_RE.search(text)
                indent = re.match(r"[ \t]*", text[mb.start():]).group(0)
                new = text[:mb.start()] + block_for(pages, i, indent) + text[mb.end():]
            else:
                mf = FOOTER_RE.search(text)
                if not mf:
                    problems.append(f"{page.relative_to(root)}: no page-footer-nav to anchor the prev/next block")
                    continue
                new = text[:mf.start()] + block_for(pages, i, mf.group(1)) + "\n" + text[mf.start():]
            if new != text:
                changed += 1
                if check:
                    problems.append(f"{page.relative_to(root)}: prev/next block is stale")
                else:
                    page.write_text(new, encoding="utf-8")

    for p in problems:
        print("ERROR:", p)
    if check:
        print(f"prev/next check: {sum(len(o) for _, o in TRACKS.values())} pages, {len(problems)} problem(s)")
    else:
        print(f"prev/next links updated on {changed} page(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv[1:]))
