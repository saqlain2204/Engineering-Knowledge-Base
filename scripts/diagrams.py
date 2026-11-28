#!/usr/bin/env python3
"""Architecture diagrams as clean inline SVG, written into site pages.

Each diagram is described below with boxes, groups and arrows. The script
computes every coordinate, then checks the layout before writing anything:

  - every label fits inside its box (measured with a wide font, so it also
    fits with narrower system fonts)
  - boxes do not overlap each other, and everything stays inside the canvas
  - each arrow starts and ends exactly on the edge of the boxes it connects
  - no arrow line passes through a box it does not connect
  - arrow labels do not cover any box or any other label

Colors come from CSS variables (see figure.diagram in styles.css), so the
same SVG works in the light and the dark theme.

The SVG goes between <!-- diagram:NAME:start --> and <!-- diagram:NAME:end -->
markers. The first time, it replaces an old ASCII drawing (a <pre> block) or is
inserted after the first paragraph of the target section.

Usage:
  python3 scripts/diagrams.py           # check layouts and write pages
  python3 scripts/diagrams.py --check   # CI: fail on a bad layout or a stale page
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Character widths of DejaVu Sans (bold and regular) in em. DejaVu is wider
# than Inter, Segoe UI, SF and Roboto, so text that fits here fits everywhere.
BOLD = {' ': 0.348, '!': 0.456, '"': 0.521, '#': 0.838, '$': 0.696, '%': 1.002, '&': 0.872, "'": 0.306, '(': 0.457, ')': 0.457, '*': 0.523, '+': 0.838, ',': 0.38, '-': 0.415, '.': 0.38, '/': 0.365, '0': 0.696, '1': 0.696, '2': 0.696, '3': 0.696, '4': 0.696, '5': 0.696, '6': 0.696, '7': 0.696, '8': 0.696, '9': 0.696, ':': 0.4, ';': 0.4, '<': 0.838, '=': 0.838, '>': 0.838, '?': 0.58, '@': 1.0, 'A': 0.774, 'B': 0.762, 'C': 0.734, 'D': 0.83, 'E': 0.683, 'F': 0.683, 'G': 0.821, 'H': 0.837, 'I': 0.372, 'J': 0.372, 'K': 0.775, 'L': 0.637, 'M': 0.995, 'N': 0.837, 'O': 0.85, 'P': 0.733, 'Q': 0.85, 'R': 0.77, 'S': 0.72, 'T': 0.682, 'U': 0.812, 'V': 0.774, 'W': 1.103, 'X': 0.771, 'Y': 0.724, 'Z': 0.725, '[': 0.457, '\\': 0.365, ']': 0.457, '^': 0.838, '_': 0.5, '`': 0.5, 'a': 0.675, 'b': 0.716, 'c': 0.593, 'd': 0.716, 'e': 0.678, 'f': 0.435, 'g': 0.716, 'h': 0.712, 'i': 0.343, 'j': 0.343, 'k': 0.665, 'l': 0.343, 'm': 1.042, 'n': 0.712, 'o': 0.687, 'p': 0.716, 'q': 0.716, 'r': 0.493, 's': 0.595, 't': 0.478, 'u': 0.712, 'v': 0.652, 'w': 0.924, 'x': 0.645, 'y': 0.652, 'z': 0.582, '{': 0.712, '|': 0.365, '}': 0.712, '~': 0.838}
REG = {' ': 0.318, '!': 0.401, '"': 0.46, '#': 0.838, '$': 0.636, '%': 0.95, '&': 0.78, "'": 0.275, '(': 0.39, ')': 0.39, '*': 0.5, '+': 0.838, ',': 0.318, '-': 0.361, '.': 0.318, '/': 0.337, '0': 0.636, '1': 0.636, '2': 0.636, '3': 0.636, '4': 0.636, '5': 0.636, '6': 0.636, '7': 0.636, '8': 0.636, '9': 0.636, ':': 0.337, ';': 0.337, '<': 0.838, '=': 0.838, '>': 0.838, '?': 0.531, '@': 1.0, 'A': 0.684, 'B': 0.686, 'C': 0.698, 'D': 0.77, 'E': 0.632, 'F': 0.575, 'G': 0.775, 'H': 0.752, 'I': 0.295, 'J': 0.295, 'K': 0.656, 'L': 0.557, 'M': 0.863, 'N': 0.748, 'O': 0.787, 'P': 0.603, 'Q': 0.787, 'R': 0.695, 'S': 0.635, 'T': 0.611, 'U': 0.732, 'V': 0.684, 'W': 0.989, 'X': 0.685, 'Y': 0.611, 'Z': 0.685, '[': 0.39, '\\': 0.337, ']': 0.39, '^': 0.838, '_': 0.5, '`': 0.5, 'a': 0.613, 'b': 0.635, 'c': 0.55, 'd': 0.635, 'e': 0.615, 'f': 0.352, 'g': 0.635, 'h': 0.634, 'i': 0.278, 'j': 0.278, 'k': 0.579, 'l': 0.278, 'm': 0.974, 'n': 0.634, 'o': 0.612, 'p': 0.635, 'q': 0.635, 'r': 0.411, 's': 0.521, 't': 0.392, 'u': 0.634, 'v': 0.592, 'w': 0.818, 'x': 0.592, 'y': 0.592, 'z': 0.525, '{': 0.636, '|': 0.337, '}': 0.636, '~': 0.838}

PAD = 12          # min space between text and box edge
TITLE_PX = 14
SUB_PX = 12
LABEL_PX = 11.5
LINE = 16         # sub-line height


def text_w(s, bold=False, px=14):
    table = BOLD if bold else REG
    return sum(table.get(ch, 0.7) for ch in s) * px


class Box:
    def __init__(self, bid, x, y, w, h, title, sub=(), cls="dg-box"):
        self.id, self.x, self.y, self.w, self.h = bid, x, y, w, h
        self.title, self.cls = title, cls
        self.sub = [sub] if isinstance(sub, str) else list(sub)

    def side(self, s, off=0):
        if s == "r": return (self.x + self.w, self.y + self.h / 2 + off)
        if s == "l": return (self.x, self.y + self.h / 2 + off)
        if s == "t": return (self.x + self.w / 2 + off, self.y)
        if s == "b": return (self.x + self.w / 2 + off, self.y + self.h)
        raise ValueError(s)

    def rect(self):
        return (self.x, self.y, self.x + self.w, self.y + self.h)


class Diagram:
    def __init__(self, name, w, h, title, desc):
        self.name, self.W, self.H, self.title, self.desc = name, w, h, title, desc
        self.boxes, self.groups, self.arrows, self.texts, self.lines = {}, [], [], [], []
        self.errors = []

    def box(self, bid, x, y, w, h, title, sub=(), cls="dg-box"):
        self.boxes[bid] = Box(bid, x, y, w, h, title, sub, cls)

    def group(self, x, y, w, h, label):
        self.groups.append((x, y, w, h, label))

    def line(self, x1, y1, x2, y2):
        self.lines.append((x1, y1, x2, y2))

    def note(self, x, y, text, anchor="middle"):
        self.texts.append((x, y, text, anchor))

    def arrow(self, a, b, fa="r", fb="l", label=None, offa=0, offb=0, both=False, hl=False, pts=None, lpos=None):
        """Arrow from box a (side fa) to box b (side fb). pts: explicit points instead."""
        self.arrows.append(dict(a=a, b=b, fa=fa, fb=fb, label=label, offa=offa, offb=offb, both=both, hl=hl, pts=pts, lpos=lpos))

    # ── geometry ──
    def route(self, ar):
        if ar["pts"]:
            return [tuple(p) for p in ar["pts"]]
        A, B = self.boxes[ar["a"]], self.boxes[ar["b"]]
        p1, p2 = A.side(ar["fa"], ar["offa"]), B.side(ar["fb"], ar["offb"])
        h1, h2 = ar["fa"] in "lr", ar["fb"] in "lr"
        if h1 and h2:
            if abs(p1[1] - p2[1]) < 0.5: return [p1, p2]
            mx = (p1[0] + p2[0]) / 2
            return [p1, (mx, p1[1]), (mx, p2[1]), p2]
        if not h1 and not h2:
            if abs(p1[0] - p2[0]) < 0.5: return [p1, p2]
            my = (p1[1] + p2[1]) / 2
            return [p1, (p1[0], my), (p2[0], my), p2]
        if h1:
            return [p1, (p2[0], p1[1]), p2]
        return [p1, (p1[0], p2[1]), p2]

    def label_rect(self, ar, pts):
        text = ar["label"]
        w, h = text_w(text, False, LABEL_PX) + 10, 18
        if ar["lpos"]:
            cx, cy = ar["lpos"]
        else:
            segs = list(zip(pts, pts[1:]))
            (x1, y1), (x2, y2) = max(segs, key=lambda s: abs(s[0][0] - s[1][0]) + abs(s[0][1] - s[1][1]))
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), (cx, cy)

    # ── checks ──
    def check(self):
        E = self.errors
        def inside_canvas(r, what):
            if r[0] < 0 or r[1] < 0 or r[2] > self.W or r[3] > self.H:
                E.append(f"{what} is outside the canvas")
        def overlap(r1, r2, gap=0):
            return r1[0] < r2[2] + gap and r2[0] < r1[2] + gap and r1[1] < r2[3] + gap and r2[1] < r1[3] + gap
        bl = list(self.boxes.values())
        for b in bl:
            inside_canvas(b.rect(), f"box {b.id}")
            need_w = max([text_w(b.title, True, TITLE_PX)] + [text_w(s, False, SUB_PX) for s in b.sub]) + 2 * PAD
            if need_w > b.w:
                E.append(f"box {b.id}: text needs {need_w:.0f}px, box is {b.w}px wide")
            need_h = 20 + LINE * len(b.sub) + 16
            if need_h > b.h:
                E.append(f"box {b.id}: text needs {need_h}px of height, box is {b.h}px")
        for i, b1 in enumerate(bl):
            for b2 in bl[i + 1:]:
                if overlap(b1.rect(), b2.rect(), 6):
                    E.append(f"boxes {b1.id} and {b2.id} overlap or touch")
        for (x, y, w, h, label) in self.groups:
            inside_canvas((x, y, x + w, y + h), f"group {label}")
            lr = (x + 10, y + 6, x + 10 + text_w(label, True, SUB_PX) * 1.15 + 6, y + 24)
            if lr[2] > x + w:
                E.append(f"group {label}: label wider than group")
            for b in bl:
                if overlap(lr, b.rect()):
                    E.append(f"group {label}: label overlaps box {b.id}")
        group_labels = [((x + 10, y + 6, x + 10 + text_w(label, True, SUB_PX) * 1.15 + 6, y + 24), label)
                        for (x, y, w, h, label) in self.groups]
        def seg_hits(p, q, r, pad=0):
            sx0, sx1 = sorted((p[0], q[0])); sy0, sy1 = sorted((p[1], q[1]))
            return sx0 < r[2] + pad and sx1 > r[0] - pad and sy0 < r[3] + pad and sy1 > r[1] - pad
        all_segs = [(i, s) for i, ar in enumerate(self.arrows) for s in zip(self.route(ar), self.route(ar)[1:])]
        all_segs += [(-1, ((x1, y1), (x2, y2))) for (x1, y1, x2, y2) in self.lines]
        for (x, y, text, anchor) in self.texts:
            w = text_w(text, False, SUB_PX)
            x0 = x - w / 2 if anchor == "middle" else x
            r = (x0, y - 12, x0 + w, y + 4)
            inside_canvas(r, f"note '{text}'")
            for b in bl:
                if overlap(r, b.rect(), 2):
                    E.append(f"note '{text}' overlaps box {b.id}")
            for _, (p, q) in all_segs:
                if _ != -1 and seg_hits(p, q, r):
                    E.append(f"note '{text}' is crossed by an arrow")
        note_rects = []
        for (x, y, text, anchor) in self.texts:
            w = text_w(text, False, SUB_PX)
            x0 = x - w / 2 if anchor == "middle" else x
            note_rects.append((x0, y - 12, x0 + w, y + 4))
        label_rects = []
        for idx, ar in enumerate(self.arrows):
            pts = self.route(ar)
            name = f"arrow {ar['a']}->{ar['b']}"
            if not ar["pts"]:
                for bid, pt, s in ((ar["a"], pts[0], ar["fa"]), (ar["b"], pts[-1], ar["fb"])):
                    b = self.boxes[bid]
                    x0, y0, x1, y1 = b.rect()
                    on_edge = (abs(pt[0] - x0) < 0.01 or abs(pt[0] - x1) < 0.01) and y0 <= pt[1] <= y1 or \
                              (abs(pt[1] - y0) < 0.01 or abs(pt[1] - y1) < 0.01) and x0 <= pt[0] <= x1
                    if not on_edge:
                        E.append(f"{name}: end point is not on the edge of {bid}")
            last = pts[-2], pts[-1]
            if abs(last[0][0] - last[1][0]) + abs(last[0][1] - last[1][1]) < 16:
                E.append(f"{name}: last segment too short for an arrowhead")
            if ar["both"]:
                first = pts[0], pts[1]
                if abs(first[0][0] - first[1][0]) + abs(first[0][1] - first[1][1]) < 16:
                    E.append(f"{name}: first segment too short for an arrowhead")
            ends = {ar["a"], ar["b"]}
            for (p, q) in zip(pts, pts[1:]):
                for b in bl:
                    if b.id in ends and not ar["pts"]:
                        continue
                    x0, y0, x1, y1 = b.rect()
                    sx0, sx1 = sorted((p[0], q[0])); sy0, sy1 = sorted((p[1], q[1]))
                    if sx0 < x1 - 1 and sx1 > x0 + 1 and sy0 < y1 - 1 and sy1 > y0 + 1:
                        E.append(f"{name}: line passes through box {b.id}")
            for (p, q) in zip(pts, pts[1:]):
                for r, gl in group_labels:
                    if seg_hits(p, q, r):
                        E.append(f"{name}: line crosses the group label {gl}")
            if ar["label"]:
                r, _ = self.label_rect(ar, pts)
                _, (lcx, lcy) = self.label_rect(ar, pts)
                for j, (p, q) in all_segs:
                    on_this = j == idx and min(p[0], q[0]) - 0.5 <= lcx <= max(p[0], q[0]) + 0.5 \
                        and min(p[1], q[1]) - 0.5 <= lcy <= max(p[1], q[1]) + 0.5
                    if not on_this and seg_hits(p, q, r):
                        E.append(f"{name}: label '{ar['label']}' is crossed by another line")
                inside_canvas(r, f"{name} label")
                for b in bl:
                    if overlap(r, b.rect(), 2):
                        E.append(f"{name}: label '{ar['label']}' overlaps box {b.id}")
                for nr in note_rects:
                    if overlap(r, nr, 8):
                        E.append(f"{name}: label '{ar['label']}' is too close to a note")
                for other in label_rects:
                    if overlap(r, other, 2):
                        E.append(f"{name}: label '{ar['label']}' overlaps another label")
                label_rects.append(r)
        return E

    # ── output ──
    def svg(self):
        n = self.name
        o = [f'<svg viewBox="0 0 {self.W} {self.H}" width="{self.W}" height="{self.H}" role="img" '
             f'aria-labelledby="dg-{n}-t dg-{n}-d" xmlns="http://www.w3.org/2000/svg">',
             f'<title id="dg-{n}-t">{html.escape(self.title)}</title>',
             f'<desc id="dg-{n}-d">{html.escape(self.desc)}</desc>',
             '<defs>',
             f'<marker id="dg-{n}-h" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="9" markerHeight="9" markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path class="dg-head" d="M0,0 L10,5 L0,10 z"/></marker>',
             f'<marker id="dg-{n}-hh" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="10" markerHeight="10" markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path class="dg-head-hl" d="M0,0 L10,5 L0,10 z"/></marker>',
             '</defs>']
        f = lambda v: (f"{v:.1f}").rstrip("0").rstrip(".")
        for (x, y, w, h, label) in self.groups:
            o.append(f'<rect class="dg-group" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="14"/>')
            o.append(f'<text class="dg-g" x="{f(x + 14)}" y="{f(y + 20)}">{html.escape(label)}</text>')
        for (x1, y1, x2, y2) in self.lines:
            o.append(f'<line class="dg-group" x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}"/>')
        for b in self.boxes.values():
            o.append(f'<rect class="{b.cls}" x="{f(b.x)}" y="{f(b.y)}" width="{f(b.w)}" height="{f(b.h)}" rx="10"/>')
            cx = b.x + b.w / 2
            total = 18 + LINE * len(b.sub)
            ty = b.y + (b.h - total) / 2 + 14
            o.append(f'<text class="dg-t" x="{f(cx)}" y="{f(ty)}" text-anchor="middle">{html.escape(b.title)}</text>')
            for i, s in enumerate(b.sub):
                o.append(f'<text class="dg-s" x="{f(cx)}" y="{f(ty + 18 + LINE * i)}" text-anchor="middle">{html.escape(s)}</text>')
        for ar in self.arrows:
            pts = self.route(ar)
            d = "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts)
            mk = f"dg-{n}-hh" if ar["hl"] else f"dg-{n}-h"
            start = f' marker-start="url(#{mk})"' if ar["both"] else ""
            o.append(f'<path class="{"dg-a-hl" if ar["hl"] else "dg-a"}" d="{d}"{start} marker-end="url(#{mk})"/>')
            if ar["label"]:
                r, (cx, cy) = self.label_rect(ar, pts)
                o.append(f'<rect class="dg-lbg" x="{f(r[0])}" y="{f(r[1])}" width="{f(r[2] - r[0])}" height="{f(r[3] - r[1])}" rx="5"/>')
                o.append(f'<text class="dg-l" x="{f(cx)}" y="{f(cy + 4)}" text-anchor="middle">{html.escape(ar["label"])}</text>')
        for (x, y, text, anchor) in self.texts:
            o.append(f'<text class="dg-s" x="{f(x)}" y="{f(y)}" text-anchor="{anchor}">{html.escape(text)}</text>')
        o.append("</svg>")
        return "\n".join(o)


# ───────────────────────── diagrams ─────────────────────────
DIAGRAMS = []


def k8s():
    d = Diagram("k8s-arch", 760, 514, "Kubernetes cluster architecture",
                "kubectl talks to the API server. The scheduler and controller manager watch the API server. "
                "Only the API server reads and writes etcd. On each worker node the kubelet watches the API server "
                "and starts pods through the container runtime. kube-proxy programs Service rules.")
    d.box("kubectl", 290, 16, 180, 46, "kubectl / CI")
    d.group(20, 86, 720, 176, "CONTROL PLANE")
    d.box("sched", 44, 118, 200, 56, "kube-scheduler", "picks a node for each pod")
    d.box("cm", 44, 190, 200, 56, "controller-manager", "reconcile loops")
    d.box("api", 290, 146, 180, 64, "kube-apiserver", "the only front door", cls="dg-hl")
    d.box("etcd", 540, 146, 180, 64, "etcd", "cluster state (key-value)", cls="dg-hl-2")
    d.arrow("kubectl", "api", "b", "t", label="HTTPS + auth")
    d.arrow("sched", "api", "r", "l", offb=-14, both=True)
    d.arrow("cm", "api", "r", "l", offb=14, both=True)
    d.arrow("api", "etcd", "r", "l", both=True, hl=True)
    for i, x in enumerate((20, 390)):
        d.group(x, 312, 350, 186, f"WORKER NODE {i + 1}")
        d.box(f"proxy{i}", x + 20, 344, 144, 56, "kube-proxy", "Service rules")
        d.box(f"kubelet{i}", x + 180, 344, 150, 56, "kubelet", "node agent")
        d.box(f"pods{i}", x + 20, 426, 144, 56, "Pods", "your containers", cls="dg-hl-3")
        d.box(f"rt{i}", x + 180, 426, 150, 56, "containerd", "runtime + CNI")
        d.arrow(f"rt{i}", f"pods{i}", "l", "r")
    d.arrow("api", "kubelet0", "b", "t", offa=-24, both=True, label="watch pods, report status", lpos=(186, 290))
    d.arrow("api", "kubelet1", "b", "t", offa=24, both=True)
    d.arrow("kubelet0", "rt0", "b", "t")
    d.arrow("kubelet1", "rt1", "b", "t")
    return d, "Docker-Kubernetes/learn/Kubernetes/kubernetes-architecture.html", "cluster-overview", ("replace-pre", 0), \
        "Everything goes through the API server. Components watch it for changes and write their results back."


def rag():
    d = Diagram("rag-pipeline", 760, 384, "RAG pipeline: ingest and query",
                "Offline, documents are split into chunks, embedded, and stored in a vector index. "
                "For each question, the question is embedded, the index returns the nearest chunks, a reranker keeps the best ones, "
                "a prompt is built with those chunks, and the LLM writes an answer with citations.")
    d.group(20, 16, 720, 116, "INGEST (WHEN DOCUMENTS CHANGE)")
    y = 52
    for i, (bid, t, s) in enumerate([("docs", "Documents", "PDF, HTML, wiki"), ("chunk", "Split", "into chunks"),
                                      ("embed", "Embed", "each chunk"), ("index", "Vector index", "+ BM25 index")]):
        d.box(bid, 40 + i * 175, y, 150, 60, t, s, cls="dg-hl-2" if bid == "index" else "dg-box")
    d.arrow("docs", "chunk"); d.arrow("chunk", "embed"); d.arrow("embed", "index")
    d.group(20, 164, 720, 204, "QUERY (EVERY QUESTION)")
    for i, (bid, t, s) in enumerate([("q", "Question", "from the user"), ("qe", "Embed", "the question"),
                                      ("search", "Search", "top 20-100"), ("rerank", "Rerank", "keep top 3-10")]):
        d.box(bid, 40 + i * 175, 200, 150, 60, t, s)
    for i, (bid, t, s) in enumerate([("ans", "Answer", "with citations"), ("llm", "LLM", "writes from context"),
                                      ("prompt", "Build prompt", "question + chunks")]):
        d.box(bid, 215 + i * 175, 290, 150, 60, t, s, cls="dg-hl" if bid == "llm" else "dg-box")
    d.arrow("q", "qe"); d.arrow("qe", "search"); d.arrow("search", "rerank")
    d.arrow("index", "search", "b", "t", label="nearest chunks")
    d.arrow("rerank", "prompt", "b", "t")
    d.arrow("prompt", "llm", "l", "r"); d.arrow("llm", "ans", "l", "r", hl=True)
    return d, "AI Engineer/learn/Prompting-and-Retrieval/ai-engineering-rag.html", "big-picture", ("replace-pre", 0), \
        "Top row runs when documents change. Bottom rows run for every question."


def vm():
    d = Diagram("vm-translate", 760, 344, "How a virtual address becomes a physical address",
                "The CPU sends a virtual address to the TLB. On a hit, the physical address goes straight to RAM. "
                "On a miss, the hardware walks the page table. If the page is present, the TLB is filled and the access continues. "
                "If not, a page fault traps to the OS, which loads the page from disk and runs the instruction again.")
    d.box("cpu", 20, 40, 130, 60, "CPU", "virtual address")
    d.box("tlb", 200, 40, 170, 60, "TLB lookup", "inside the MMU", cls="dg-hl")
    d.box("pa", 430, 40, 172, 60, "Physical address", "frame + offset")
    d.box("ram", 640, 40, 100, 60, "RAM")
    d.box("walk", 200, 150, 170, 60, "Page table walk", "4 levels on x86-64")
    d.box("fault", 200, 262, 170, 60, "Page fault", "trap into the kernel", cls="dg-hl-3")
    d.box("os", 440, 262, 300, 60, "OS loads the page from disk", "updates the page table, retries")
    d.arrow("cpu", "tlb")
    d.arrow("tlb", "pa", label="hit", hl=True)
    d.arrow("pa", "ram", hl=True)
    d.arrow("tlb", "walk", "b", "t", label="miss")
    d.arrow("walk", "pa", "r", "b", label="present: fill TLB")
    d.arrow("walk", "fault", "b", "t", label="not in RAM")
    d.arrow("fault", "os")
    return d, "CS-Fundamentals/learn/Operating-Systems/os-virtual-memory-paging.html", "tlb", ("after-p", 1), \
        "Most accesses take the top path. A page fault costs microseconds to milliseconds, so it must be rare."


def lb():
    d = Diagram("lb-topology", 760, 316, "Load balancer topology",
                "Clients connect over HTTPS to a layer 4 load balancer, which spreads TCP connections across layer 7 reverse proxies. "
                "The proxy terminates TLS, reads each HTTP request, runs health checks, and sends each request to one of three app servers.")
    d.box("clients", 20, 122, 120, 70, "Clients", "browsers, apps")
    d.box("l4", 200, 122, 170, 70, "L4 load balancer", ["TCP connections", "very fast"])
    d.box("l7", 420, 122, 170, 70, "L7 reverse proxy", ["TLS, HTTP routing", "health checks"], cls="dg-hl")
    d.group(616, 16, 134, 284, "APP POOL")
    d.box("a1", 632, 52, 104, 56, "app-1", "healthy")
    d.box("a2", 632, 129, 104, 56, "app-2", "healthy")
    d.box("a3", 632, 206, 104, 56, "app-3", "slow", cls="dg-hl-3")
    d.arrow("clients", "l4", label="HTTPS")
    d.arrow("l4", "l7", label="TCP")
    d.arrow("l7", "a1", offa=-22)
    d.arrow("l7", "a2")
    d.arrow("l7", "a3", offa=22)
    return d, "CS-Fundamentals/learn/Computer-Networks/cn-load-balancing-reverse-proxies.html", "layers", ("after-p", 0), \
        "A layer 4 balancer only sees connections. The layer 7 proxy sees each request, so it can route by path and skip a slow server."


def llm():
    d = Diagram("llm-serving", 760, 300, "How an LLM server handles a request",
                "Requests enter a scheduler that does continuous batching. Prefill reads the whole prompt in one pass, "
                "writes keys and values to the paged KV cache, and makes the first token. Decode then makes one token per step, "
                "reading and appending to the KV cache, and streams tokens back to the user.")
    d.box("req", 20, 40, 130, 60, "Requests", "prompts arrive")
    d.box("sched", 200, 40, 170, 60, "Scheduler", "continuous batching")
    d.box("prefill", 420, 40, 160, 60, "Prefill", "whole prompt, 1 pass", cls="dg-hl")
    d.box("decode", 420, 190, 160, 60, "Decode", "1 token per step", cls="dg-hl")
    d.box("kv", 626, 110, 120, 70, "KV cache", "paged blocks", cls="dg-hl-2")
    d.box("out", 200, 190, 170, 60, "Token stream", "sent to the user")
    d.arrow("req", "sched"); d.arrow("sched", "prefill")
    d.arrow("prefill", "decode", "b", "t", label="first token")
    d.arrow("prefill", "kv", "r", "t", label="write K, V")
    d.arrow("decode", "kv", "r", "b", both=True, label="read + append")
    d.arrow("decode", "out", "l", "r", hl=True)
    return d, "AI Engineer/learn/Inference-Deployment-Operations/ai-engineering-inference-optimization.html", "how-generation-works", ("after-pre", 0), \
        "Prefill is compute-bound. Decode is memory-bound: every step reads the weights and the whole KV cache."


def tls():
    d = Diagram("tls13", 760, 440, "TLS 1.3 handshake",
                "The client sends ClientHello with its key share and SNI. The server answers with ServerHello and its key share. "
                "Both sides now share a secret, so the server's EncryptedExtensions, Certificate, CertificateVerify and Finished are encrypted. "
                "The client checks the certificate, then sends Finished together with its first HTTP request. One round trip in total.")
    d.box("c", 40, 16, 150, 46, "Client")
    d.box("s", 570, 16, 150, 46, "Server")
    d.line(115, 62, 115, 424)
    d.line(645, 62, 645, 424)
    rows = [
        (100, "c", "ClientHello: key share, SNI, ciphers", False),
        (150, "s", "ServerHello: server key share", False),
        (236, "s", "Certificate + CertificateVerify", True),
        (282, "s", "Finished", True),
        (358, "c", "Finished + GET /", True),
        (404, "s", "HTTP response", True),
    ]
    for y, frm, text, enc in rows:
        x1, x2 = (115, 645) if frm == "c" else (645, 115)
        d.arrow("c", "s", pts=[(x1, y), (x2, y)], label=text, hl=enc, lpos=(380, y - 13))
    d.note(380, 194, "from here on, everything is encrypted")
    d.note(124, 318, "client checks chain, name, dates", anchor="start")
    return d, "CS-Fundamentals/learn/Computer-Networks/cn-tls-https-certificates.html", "handshake", ("replace-pre", 1), \
        "Colored arrows carry encrypted data. The client can send its request after one round trip."


DIAGRAMS = [k8s, rag, vm, lb, llm, tls]


def figure(name, svg, caption):
    return (f'<!-- diagram:{name}:start -->\n'
            f'<figure class="diagram" id="fig-{name}">\n<div class="dg-scroll">\n{svg}\n</div>\n'
            f'<figcaption>{html.escape(caption)}</figcaption>\n</figure>\n'
            f'<!-- diagram:{name}:end -->')


def place(text, name, section, how, block):
    start, end = f"<!-- diagram:{name}:start -->", f"<!-- diagram:{name}:end -->"
    if start in text:
        return re.sub(re.escape(start) + r"[\s\S]*?" + re.escape(end), lambda m: block, text, count=1)
    m = re.search(r'<section id="' + re.escape(section) + r'">([\s\S]*?)</section>', text)
    if not m:
        raise SystemExit(f"section #{section} not found for diagram {name}")
    body, base = m.group(1), m.start(1)
    kind, idx = how
    if kind == "replace-pre":
        pres = list(re.finditer(r"<pre>[\s\S]*?</pre>", body))
        p = pres[idx]
        return text[:base + p.start()] + block + text[base + p.end():]
    tag = {"after-p": r"</p>", "after-pre": r"</pre>"}[kind]
    ends = list(re.finditer(tag, body))
    e = ends[idx]
    return text[:base + e.end()] + "\n    " + block + text[base + e.end():]


def main():
    check = "--check" in sys.argv
    bad, stale = 0, []
    for fn in DIAGRAMS:
        d, page, section, how, caption = fn()
        errs = d.check()
        for e in errs:
            print(f"LAYOUT {d.name}: {e}")
        bad += len(errs)
        path = ROOT / page
        text = path.read_text(encoding="utf-8")
        new = place(text, d.name, section, how, figure(d.name, d.svg(), caption))
        if new != text:
            stale.append(page)
            if not check and not errs:
                path.write_text(new, encoding="utf-8")
    if check:
        for s in stale:
            print("stale diagram in", s)
    print(f"{len(DIAGRAMS)} diagrams, {bad} layout problem(s), {len(stale)} page(s) {'stale' if check else 'updated'}")
    return 1 if bad or (check and stale) else 0


if __name__ == "__main__":
    sys.exit(main())
