#!/usr/bin/env python3
"""Detect typosquatted dependencies: common misspellings of popular packages."""

import sys
from pathlib import Path

SQUATS = {
    "requests": ["reqeusts", "request", "requests2", "requests3"],
    "urllib3": ["urllib", "urlib3", "urllib2", "urllib3-fake"],
    "numpy": ["numpi", "numpyy", "num-py", "numpy2"],
    "pandas": ["pandass", "panda", "pandas2", "pd-pandas"],
    "django": ["djano", "djanga", "django2", "djangoo"],
    "flask": ["flas", "flaskk", "flask2", "flask-app"],
    "pytest": ["pytests", "py-test", "pytest2", "pytest-fake"],
    "black": ["blak", "blackk", "black-formatter"],
    "mypy": ["mypi", "mypyy", "my-py"],
    "ruff": ["ruf", "rufff", "ruff-linter"],
}

def audit() -> int:
    req = Path("requirements.txt")
    if not req.exists():
        print("ℹ️  No requirements.txt found.")
        return 0
    
    installed = {line.split("==")[0].lower() for line in req.read_text().splitlines() if "==" in line}
    
    hits = 0
    for legit, squats in SQUATS.items():
        for dep in installed:
            if dep in squats:
                print(f"🚨 TYPOQUAT DETECTED: '{dep}' (did you mean '{legit}'?)")
                hits += 1
            # Levenshtein distance check for close matches
            if len(dep) > 3 and abs(len(dep) - len(legit)) <= 2:
                # Simple character difference count
                diff = sum(a != b for a, b in zip(dep, legit))
                if diff <= 2 and dep != legit:
                    print(f"⚠️  SUSPICIOUS: '{dep}' looks like '{legit}' (diff={diff})")
                    hits += 1
    
    if hits:
        print(f"\n❌ {hits} potential typosquat(s). Verify package authenticity on PyPI.")
        return 1
    print("✅ No typosquatted dependencies detected.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
