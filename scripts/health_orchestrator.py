#!/usr/bin/env python3
"""Master orchestrator: run all health checks in dependency order and emit final verdict."""

import subprocess
import sys
from pathlib import Path

PIPELINE = [
    ("workspace", ["python", "scripts/workspace_audit.py"]),
    ("tests", ["python", "scripts/test_parallel.py"]),
    ("coverage", ["python", "scripts/alert_threshold.py"]),
    ("lint", ["python", "scripts/lint_report.py"]),
    ("security", ["python", "scripts/secret_scan.py"]),
    ("deps", ["python", "scripts/audit_deps.py"]),
    ("health", ["python", "scripts/health_score.py"]),
    ("trend", ["python", "scripts/health_trend.py"]),
    ("compare", ["python", "scripts/health_compare.py"]),
]

def orchestrate() -> int:
    results = {}
    for name, cmd in PIPELINE:
        print(f"\\n{'='*50}\\n🔷 {name.upper()}\\n{'='*50}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        ok = result.returncode == 0
        results[name] = ok
        print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
        if not ok and result.stderr:
            print(result.stderr[-500:])
        print(f"{'✅ PASS' if ok else '❌ FAIL'}")
    
    passed = sum(results.values())
    total = len(results)
    print(f"\\n{'='*50}\\nFINAL: {passed}/{total} stages passed")
    for name, ok in results.items():
        print(f"  {'✅' if ok else '❌'} {name}")
    
    # Trigger alert if health stage failed
    if not results.get("health", True):
        subprocess.run(["python", "scripts/health_alert.py"], capture_output=True)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(orchestrate())
