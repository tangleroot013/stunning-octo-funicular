#!/usr/bin/env python3
"""Composite security score from all security audits. 0-100."""

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
]

def score() -> int:
    results = {}
    for name, cmd in AUDITS:
        result = subprocess.run(cmd, capture_output=True)
        results[name] = result.returncode == 0
    
    passed = sum(results.values())
    total = len(results)
    score = int(passed / total * 100)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "score": score,
        "passed": passed,
        "total": total,
        "checks": results,
    }
    
    Path(".security_score").write_text(str(score))
    Path("SECURITY_REPORT.json").write_text(json.dumps(report, indent=2))
    
    print(f"# Security Score: {score}/100\n")
    for name, ok in results.items():
        print(f"  {'✅' if ok else '❌'} {name}")
    
    color = "brightgreen" if score >= 90 else "yellow" if score >= 70 else "red"
    print(f"\n{'🛡️  SECURE' if score >= 90 else '⚠️  VULNERABLE' if score < 70 else '🔒 ACCEPTABLE'}")
    return 0 if score >= 70 else 1

if __name__ == "__main__":
    sys.exit(score())
