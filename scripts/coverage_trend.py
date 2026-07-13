#!/usr/bin/env python3
"""Track coverage delta across runs using .last_cov_score history."""

import json
from pathlib import Path

HISTORY = Path(".coverage_history.json")

def record() -> None:
    score = Path(".last_cov_score").read_text().strip()
    entry = {"score": float(score), "trend": "flat"}
    if HISTORY.exists():
        hist = json.loads(HISTORY.read_text())
        prev = hist[-1]["score"] if hist else float(score)
        entry["trend"] = "up" if float(score) > prev else "down" if float(score) < prev else "flat"
    else:
        hist = []
    hist.append(entry)
    HISTORY.write_text(json.dumps(hist[-50:], indent=2))  # rolling window
    print(f"📈 Coverage {entry['trend']}: {score}%")

if __name__ == "__main__":
    record()
