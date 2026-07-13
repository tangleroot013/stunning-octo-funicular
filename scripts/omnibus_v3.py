#!/usr/bin/env python3
"""Ultimate omnibus: parallel execution, JSON report, HTML dashboard, and exit gating."""

import concurrent.futures
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

CHECKS = [
    ("workspace", [sys.executable, "scripts/workspace_audit.py"]),
    ("tests", [sys.executable, "scripts/test_parallel.py"]),
    ("coverage", [sys.executable, "scripts/alert_threshold.py"]),
    ("lint", [sys.executable, "scripts/lint_report.py"]),
    ("security", [sys.executable, "scripts/secret_scan.py"]),
    ("deps", [sys.executable, "scripts/audit_deps.py"]),
    ("docker", [sys.executable, "scripts/docker_ready.py"]),
    ("naming", [sys.executable, "scripts/test_naming.py"]),
    ("types", [sys.executable, "scripts/typing_strict.py"]),
    ("branch", [sys.executable, "scripts/branch_protect.py"]),
    ("perf", [sys.executable, "scripts/perf_regression.py"]),
    ("health", [sys.executable, "scripts/health_score.py"]),
]

def run_check(name_cmd):
    name, cmd = name_cmd
    t0 = datetime.now()
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "name": name,
        "pass": result.returncode == 0,
        "stdout": result.stdout[-300:],
        "stderr": result.stderr[-200:],
        "duration_ms": int((datetime.now() - t0).total_seconds() * 1000),
    }

def html_report(report: dict) -> str:
    rows = ""
    for c in report["checks"]:
        color = "#2ecc71" if c["pass"] else "#e74c3c"
        rows += f'<tr style="background:{color}22"><td>{c["name"]}</td><td>{"PASS" if c["pass"] else "FAIL"}</td><td>{c["duration_ms"]}ms</td></tr>'
    
    return f"""<!DOCTYPE html>
<html><head><title>SOF Dashboard</title><style>
body{{font-family:system-ui;max-width:800px;margin:40px auto;padding:20px}}
table{{width:100%;border-collapse:collapse}}th,td{{padding:10px;text-align:left;border-bottom:1px solid #ddd}}
h1{{color:#333}}.meta{{color:#666;font-size:14px}}
</style></head><body>
<h1>🚀 stunning-octo-funicular Dashboard</h1>
<p class="meta">{report["timestamp"]} | {report["passed"]}/{report["total"]} passed</p>
<table><tr><th>Check</th><th>Status</th><th>Time</th></tr>{rows}</table>
</body></html>"""

def main() -> int:
    print("🚀 Omnibus v3 — Parallel Execution Engine\n")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(run_check, CHECKS))
    
    passed = sum(1 for r in results if r["pass"])
    report = {
        "timestamp": datetime.now().isoformat(),
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "checks": results,
    }
    
    Path("OMNIBUS_V3.json").write_text(json.dumps(report, indent=2))
    Path("OMNIBUS_V3.html").write_text(html_report(report))
    
    print(f"\n{'='*50}")
    for r in sorted(results, key=lambda x: -x["duration_ms"]):
        icon = "✅" if r["pass"] else "❌"
        print(f"{icon} {r['name']:<15} {r['duration_ms']:>5}ms")
    
    print(f"\n{'='*50}")
    status = "🟢 ALL CLEAR" if passed == len(results) else "🔴 FAILURES DETECTED"
    print(f"{status}: {passed}/{len(results)}")
    print(f"📄 OMNIBUS_V3.json  📊 OMNIBUS_V3.html")
    
    return 0 if passed == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())
