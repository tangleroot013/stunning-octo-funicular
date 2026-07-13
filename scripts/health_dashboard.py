#!/usr/bin/env python3
"""Aggregate .last_* dotfiles into a single JSON health report."""

import json
from datetime import datetime
from pathlib import Path

def read_dot(name: str) -> str:
    p = Path(f".last_{name}")
    return p.read_text().strip() if p.exists() else "unknown"

def build() -> None:
    report = {
        "timestamp": datetime.now().isoformat(),
        "coverage_score": read_dot("cov_score"),
        "runtime_ms": read_dot("runtime"),
        "tests_passed": Path(".last_test_ok").exists(),
        "audit": json.loads(Path("audit.json").read_text()) if Path("audit.json").exists() else {},
    }
    Path("health_dashboard.json").write_text(json.dumps(report, indent=2))
    print("✅ health_dashboard.json written.")

if __name__ == "__main__":
    build()
