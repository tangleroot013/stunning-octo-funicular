#!/usr/bin/env python3
"""Master integrity orchestrator: run all security, compliance, and supply chain audits."""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

AUDITS = [
    ("security", ["python", "scripts/security_orchestrator.py"]),
    ("supply_chain", ["python", "scripts/supply_chain.py"]),
    ("pii", ["python", "scripts/pii_scan.py"]),
    ("crypto", ["python", "scripts/crypto_audit.py"]),
    ("random", ["python", "scripts/random_audit.py"]),
    ("timeout", ["python", "scripts/timeout_audit.py"]),
    ("exception_leak", ["python", "scripts/exception_leak.py"]),
    ("debug_flag", ["python", "scripts/debug_flag.py"]),
    ("mfa", ["python", "scripts/mfa_audit.py"]),
    ("audit_log", ["python", "scripts/audit_log.py"]),
    ("idor", ["python", "scripts/idor_detect.py"]),
    ("race", ["python", "scripts/race_condition.py"]),
    ("permissions", ["python", "scripts/permissions_audit.py"]),
    ("zero_trust", ["python", "scripts/zero_trust.py"]),
]

def orchestrate() -> int:
    print("🔐 Integrity Orchestrator v1.0\n")
    results = {}
    
    for name, cmd in AUDITS:
        print(f"{'─'*50}")
        print(f"🔒 {name}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        ok = result.returncode == 0
        results[name] = {
            "pass": ok,
            "output": result.stdout[-400:] if result.stdout else "",
        }
        print(f"{'✅ PASS' if ok else '❌ FAIL'}")
        if not ok and result.stdout:
            print(result.stdout[-200:])
    
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
    
    Path("INTEGRITY_REPORT.json").write_text(json.dumps(report, indent=2))
    
    print(f"\n{'='*50}")
    print(f"INTEGRITY SCORE: {score}/100")
    print(f"{'🛡️  FORTRESS' if score >= 95 else '🔒 HARDENED' if score >= 85 else '⚠️  VULNERABLE' if score < 70 else '🔐 ACCEPTABLE'}")
    print(f"📄 INTEGRITY_REPORT.json")
    
    return 0 if score >= 70 else 1

if __name__ == "__main__":
    sys.exit(orchestrate())
