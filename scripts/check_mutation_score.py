"""Validate mutmut 2.x terminal summary against the lab 5 quality gate."""
import re
import sys
from pathlib import Path

log = Path(sys.argv[1] if len(sys.argv) > 1 else "mutation-run.log")
raw = log.read_text(encoding="utf-8", errors="replace")
# mutmut emits progress updates with carriage returns and ANSI escape codes.
clean = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", raw)
progress = list(
    re.finditer(
        r"(\d+)\s*/\s*(\d+)\s*🎉\s*(\d+)\s*⏰\s*(\d+)"
        r"\s*🤔\s*(\d+)\s*🙁\s*(\d+)\s*🔇\s*(\d+)",
        clean,
    )
)
if not progress:
    raise SystemExit("No complete mutmut progress summary found; refusing to pass.")
processed, total, killed, timeout, suspicious, survived, skipped = map(
    int, progress[-1].groups()
)
if processed != total or total == 0:
    raise SystemExit(f"Incomplete mutation run: {processed}/{total}")
if killed + timeout + suspicious + survived + skipped != total:
    raise SystemExit("Mutation categories do not sum to the total")
# Only clearly killed mutants count as detected; no credit for timeouts.
denominator = killed + survived + timeout + suspicious
if denominator == 0:
    raise SystemExit("No applicable mutations to score")
score = killed / denominator * 100
summary = (
    f"Mutation score: {killed}/{denominator} = {score:.1f}% "
    f"(survived={survived}, timeout={timeout}, suspicious={suspicious}, "
    f"skipped={skipped}); threshold=70%"
)
print(summary)
Path("mutation-score.txt").write_text(summary + "\n", encoding="utf-8")
if score < 70:
    raise SystemExit("Mutation score is below the 70% quality gate")
