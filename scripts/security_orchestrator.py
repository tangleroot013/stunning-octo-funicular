#!/usr/bin/env python3
"""Master security orchestrator: run all security audits and emit unified report."""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

AUDITS = [
    ("secrets", ["python", "scripts/secret_scan.py"]),
    ("hmac", ["python", "scripts/hmac_verify.py"]),
    ("sandbox", ["python", "scripts/sandbox_audit.py"]),
    ("tls", ["python", "scripts/tls_audit.py"]),
    ("pickle", ["python", "scripts/pickle_audit.py"]),
    ("tempfile", ["python", "scripts/tempfile_audit.py"]),
    ("jwt", ["python", "scripts/jwt_audit.py"]),
    ("sql_inject", ["python", "scripts/sql_inject.py"]),
    ("path_traversal", ["python", "scripts/path_traversal.py"]),
    ("csp", ["python", "scripts/csp_audit.py"]),
    ("permissions", ["python", "scripts/permissions_audit.py"]),
    ("cve", ["python", "scripts/cve_check.py"]),
    ("rotation", ["python", "scripts/secret_rotation.py"]),
    ("pins", ["python", "scripts/dependency_pin.py"]),
    ("network", ["python", "scripts/network_bind.py"]),
    ("session", ["python", "scripts/session_audit.py"]),
    ("headers", ["python", "scripts/header_audit.py"]),
]

def orchestrate() -> int:
    print("🛡️  Security Orchestrator v1.0\n")
    results = {}
    
    for name, cmd in AUDITS:
        print(f"{'─'*40}")
        print(f"🔒 {name}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        ok = result.returncode == 0
        results[name] = {
            "pass": ok,
            "output": result.stdout[-500:] if result.stdout else "",
        }
        print(f"{'✅ PASS' if ok else '❌ FAIL'}")
        if not ok and result.stdout:
            print(result.stdout[-300:])
    
    passed = sum(1 for r in results.values() if r["pass"])
    total = len(results)
    score = int(passed / total * 100)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "score": score,
        "passed": passed,
        "total": total,
        "checks": results,
    }
    
    Path("SECURITY_ORCHESTRATOR.json").write_text(json.dumps(report, indent=2))
    
    print(f"\n{'='*40}")
    print(f"SECURITY SCORE: {score}/100")
    print(f"{'🛡️  FORTRESS' if score >= 95 else '🔒 HARDENED' if score >= 85 else '⚠️  VULNERABLE' if score < 70 else '🔐 ACCEPTABLE'}")
    print(f"📄 SECURITY_ORCHESTRATOR.json")
    
    return 0 if score >= 70 else 1

if __name__ == "__main__":
    sys.exit(orchestrate())
