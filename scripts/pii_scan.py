#!/usr/bin/env python3
"""GDPR-style PII detector: emails, SSNs, phone numbers, credit cards in source and logs."""

import re
import sys
from pathlib import Path

PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "phone": re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d{4}[- ]?){3}\d{4}\b"),
    "ip_address": re.compile(r"\b(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}\b"),
}

def audit() -> int:
    hits = 0
    for root in ("src", "tests", "scripts", "."):
        for f in Path(root).rglob("*"):
            if f.is_file() and f.stat().st_size < 1_000_000 and ".git" not in str(f):
                try:
                    text = f.read_text(errors="ignore")
                except Exception:
                    continue
                for pii_type, pat in PATTERNS.items():
                    for m in pat.finditer(text):
                        line = text[:m.start()].count("\n") + 1
                        print(f"🚨 {f}:{line} {pii_type}: {m.group()[:30]}...")
                        hits += 1
                        if hits >= 50:
                            break
    if hits:
        print(f"\n❌ {hits} PII occurrence(s). Redact or tokenize before commit.")
        return 1
    print("✅ No PII detected in repository.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
