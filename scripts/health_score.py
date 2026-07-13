#!/usr/bin/env python3
"""Composite health score from all dotfiles, reports, and checks. 0-100."""

import json
import subprocess
import sys
from pathlib import Path

WEIGHTS = {
    "tests": 25,
    "coverage": 20,
    "lint": 15,
    "security": 15,
    "docs": 10,
    "types": 10,
    "performance": 5,
}

def score() -> int:
    scores = {k: 0 for k in WEIGHTS}
    
    # Tests
    if Path(".last_test_ok").exists():
        scores["tests"] = 100
    
    # Coverage
    cov_file = Path(".last_cov_score")
    if cov_file.exists():
        scores["coverage"] = min(float(cov_file.read_text().strip()), 100)
    
    # Lint
    lint_file = Path("lint_report.md")
    if lint_file.exists() and "FAIL" not in lint_file.read_text():
        scores["lint"] = 100
    
    # Security
    sec_result = subprocess.run([sys.executable, "scripts/secret_scan.py"], capture_output=True)
    scores["security"] = 100 if sec_result.returncode == 0 else 0
    
    # Docs
    if Path("API_INDEX.md").exists() and Path("CHANGELOG.md").exists():
        scores["docs"] = 100
    
    # Types
    type_file = Path("type_check.json")
    if type_file.exists():
        try:
            data = json.loads(type_file.read_text())
            scores["types"] = 100 if data.get("status") == "pass" else 50
        except Exception:
            pass
    
    # Performance
    perf_file = Path(".last_runtime")
    if perf_file.exists():
        rt = float(perf_file.read_text().strip())
        scores["performance"] = 100 if rt < 5000 else max(0, 100 - (rt - 5000) / 100)
    
    total = sum(scores[k] * WEIGHTS[k] / 100 for k in WEIGHTS)
    
    print(f"# Health Score: {total:.0f}/100\\n")
    for k, v in scores.items():
        bar = "█" * int(v / 5) + "░" * (20 - int(v / 5))
        print(f"{k:12} {bar} {v:.0f}% (weight: {WEIGHTS[k]})")
    
    Path(".health_score").write_text(str(int(total)))
    print(f"\\n{'🟢 Healthy' if total >= 80 else '🟡 Needs attention' if total >= 60 else '🔴 Critical'}")
    return 0 if total >= 60 else 1

if __name__ == "__main__":
    sys.exit(score())
