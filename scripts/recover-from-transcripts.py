import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
td = root / "agent-transcripts"
em = "\u2014"

# 1) Restore from Write tool calls
writes = {}
for tf in td.glob("**/*.jsonl"):
    with open(tf, encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            for part in obj.get("message", {}).get("content", []):
                if part.get("type") == "tool_use" and part.get("name") == "Write":
                    p = part.get("input", {}).get("path", "")
                    c = part.get("input", {}).get("contents", "")
                    if p and c:
                        writes[p] = c

restored = 0
for path_str, content in writes.items():
    p = Path(path_str)
    if not p.exists():
        continue
    if p.stat().st_size > 0 and "Interview-Preparations" in path_str:
        # still fix em dashes in non-empty files later
        pass
    if p.stat().st_size == 0:
        p.write_text(content.replace(em, " - "), encoding="utf-8")
        restored += 1
        print(f"Restored empty: {p.relative_to(root)}")

print(f"Restored {restored} empty files from writes")

# 2) Fix em dashes in all HTML under root
fixed = 0
for html in root.rglob("*.html"):
    text = html.read_text(encoding="utf-8")
    if em in text:
        html.write_text(text.replace(em, " - "), encoding="utf-8")
        fixed += 1
        print(f"Fixed em dash: {html.relative_to(root)}")

print(f"Fixed em dashes in {fixed} files")

# 3) Report still-empty learn files
empty = [p for p in root.rglob("*.html") if p.stat().st_size == 0]
if empty:
    print("Still empty:")
    for p in empty:
        print(f"  {p.relative_to(root)}")
