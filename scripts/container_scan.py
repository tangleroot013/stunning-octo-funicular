#!/usr/bin/env python3
"""Scan Dockerfile for security anti-patterns: latest tags, root user, secrets."""

import re
import sys
from pathlib import Path

def audit() -> int:
    df = Path("Dockerfile")
    if not df.exists():
        print("ℹ️  No Dockerfile found.")
        return 0
    
    text = df.read_text()
    lines = text.splitlines()
    hits = 0
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Check for latest tag
        if re.match(r"^FROM\s+\S+:latest", stripped, re.IGNORECASE):
            print(f"🚨 {i}: 'latest' tag — pin to specific version")
            hits += 1
        
        # Check for root user
        if re.match(r"^USER\s+root", stripped, re.IGNORECASE):
            print(f"🚨 {i}: running as root — create non-root user")
            hits += 1
        
        # Check for secrets in ENV
        if re.match(r"^ENV\s+(API_KEY|SECRET|TOKEN|PWD|PASSWORD)", stripped, re.IGNORECASE):
            print(f"🚨 {i}: secret in ENV — use secrets manager or build args")
            hits += 1
        
        # Check for ADD vs COPY
        if re.match(r"^ADD\s+", stripped, re.IGNORECASE):
            print(f"⚠️  {i}: ADD used — prefer COPY for local files")
            hits += 1
        
        # Check for sudo
        if "sudo" in stripped.lower():
            print(f"🚨 {i}: sudo detected — unnecessary in containers")
            hits += 1
    
    # Check for .dockerignore
    if not Path(".dockerignore").exists():
        print(f"⚠️  No .dockerignore — sensitive files may leak into image")
        hits += 1
    
    if hits:
        print(f"\n❌ {hits} Dockerfile security issue(s).")
        return 1
    print("✅ Dockerfile security posture clean.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
