"""Ensure every MoSCoW Must requirement has a nonempty test/plan mapping."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
requirements = (root / "docs/requirements.md").read_text(encoding="utf-8")
matrix = (root / "docs/testing/traceability.md").read_text(encoding="utf-8")
must = set(re.findall(r"^\|\s*(FR-\d{2})\s*\|\s*Must\s*\|", requirements, re.MULTILINE))
if not must:
    raise SystemExit("No Must requirements found in requirements.md")

mapped = {}
for line in matrix.splitlines():
    match = re.match(r"^\|\s*(FR-\d{2})\s+—[^|]*\|([^|]*)\|([^|]*)\|([^|]*)\|", line)
    if match:
        mapped[match.group(1)] = [part.strip() for part in match.groups()[1:]]

missing = sorted(req for req in must if req not in mapped or not all(mapped[req]))
if missing:
    raise SystemExit(f"Missing traceability mapping for Must: {', '.join(missing)}")
print(f"Must traceability: {len(must)}/{len(must)} mapped (not necessarily implemented)")
