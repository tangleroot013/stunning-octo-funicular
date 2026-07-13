#!/usr/bin/env python3
"""Next-gen omnibus: run ALL checks in parallel and emit a unified JSON report."""

import concurrent.futures
import json
import subprocess
import sys
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
]

def run_check(name_cmd):
    name, cmd = name_cmd
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "name": name,
        "pass": result.returncode == 0,
        "stdout": result.stdout[-500:],
        "stderr": result.stderr[-200:],
        "duration_ms": 0,
    }

def main() -> int:
    print("🚀 Running omnibus v2 (parallel)...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(run_check, CHECKS))
    
    passed = sum(1 for r in results if r["pass"])
    report = {
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "checks": results,
    }
    
    Path("OMNIBUS_V2.json").write_text(json.dumps(report, indent=2))
    print(f"\\n{'✅' if passed == len(results) else '❌'} {passed}/{len(results)} passed")
    print(f"📄 Report: OMNIBUS_V2.json")
    return 0 if passed == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())
