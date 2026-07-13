#!/usr/bin/env python3
"""Validate git user.email and user.name are set and match a corporate domain pattern."""

import re
import subprocess
import sys
from pathlib import Path

DOMAIN_RE = re.compile(r"@([a-zA-Z0-9.-]+\\.[a-zA-Z]{2,})$")

def check() -> int:
    name = subprocess.check_output(["git", "config", "user.name"], text=True).strip()
    email = subprocess.check_output(["git", "config", "user.email"], text=True).strip()
    if not name or not email:
        print("❌ Git identity incomplete. Set user.name and user.email.")
        return 1
    m = DOMAIN_RE.search(email)
    if not m:
        print(f"❌ Invalid email format: {email}")
        return 1
    domain = m.group(1)
    print(f"✅ Identity: {name} <{email}> (domain: {domain})")
    # Check against settings.json if email domain is specified
    settings = Path("settings.json")
    if settings.exists():
        data = __import__("json").loads(settings.read_text())
        allowed = data.get("repository", {}).get("allowed_email_domains", [])
        if allowed and domain not in allowed:
            print(f"❌ Domain '{domain}' not in allowed list: {allowed}")
            return 1
    return 0

if __name__ == "__main__":
    sys.exit(check())
