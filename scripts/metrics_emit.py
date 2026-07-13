#!/usr/bin/env python3
"""Emit workspace metrics in Prometheus text format for scraping."""

import json
from pathlib import Path
from datetime import datetime

def emit() -> None:
    lines = [
        "# HELP sof_health_score Composite workspace health score",
        "# TYPE sof_health_score gauge",
    ]
    
    score_file = Path(".health_score")
    score = int(score_file.read_text().strip()) if score_file.exists() else 0
    lines.append(f'sof_health_score{{repo="stunning-octo-funicular"}} {score}')
    
    cov_file = Path(".last_cov_score")
    cov = float(cov_file.read_text().strip()) if cov_file.exists() else 0
    lines.extend([
        "# HELP sof_coverage_percent Test coverage percentage",
        "# TYPE sof_coverage_percent gauge",
        f'sof_coverage_percent{{repo="stunning-octo-funicular"}} {cov}',
    ])
    
    rt_file = Path(".last_runtime")
    rt = float(rt_file.read_text().strip()) if rt_file.exists() else 0
    lines.extend([
        "# HELP sof_test_runtime_ms Last test runtime in milliseconds",
        "# TYPE sof_test_runtime_ms gauge",
        f'sof_test_runtime_ms{{repo="stunning-octo-funicular"}} {rt}',
    ])
    
    out = Path("metrics.prom")
    out.write_text("\n".join(lines) + "\n")
    print(f"✅ metrics.prom written ({len(lines)} lines)")

if __name__ == "__main__":
    emit()
