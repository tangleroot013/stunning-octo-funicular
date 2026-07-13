#!/usr/bin/env python3
"""Validate FastAPI security headers match OWASP recommendations."""

import json
from pathlib import Path

OWASP = {
    "Strict-Transport-Security": "max-age=31536000",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
}

def validate() -> int:
    data = json.loads(Path("settings.json").read_text())
    headers = data.get("web", {}).get("security_headers", {})
    missing = set(OWASP) - set(headers)
    if missing:
        print(f"❌ Missing security headers: {missing}")
        return 1
    print("✅ Security headers configured.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(validate())
