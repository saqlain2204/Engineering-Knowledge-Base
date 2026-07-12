import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
scan = root / (sys.argv[1] if len(sys.argv) > 1 else "Docker-Kubernetes")
broken = []
for html in scan.rglob("*.html"):
    text = html.read_text(encoding="utf-8")
    for m in re.finditer(r'href="([^"#]+)"', text):
        href = m.group(1)
        if href.startswith(("http", "mailto:", "javascript:")):
            continue
        target = (html.parent / href).resolve()
        if not target.exists():
            broken.append((str(html.relative_to(root)), href))

for src, href in sorted(set(broken)):
    print(f"{src} -> {href}")
print(f"total broken: {len(set(broken))}")
