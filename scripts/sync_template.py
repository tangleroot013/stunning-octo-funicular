#!/usr/bin/env python3
"""Warn if scaffold templates diverge from upstream reference."""

import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

TEMPLATE_DIR = Path("templates")
REF_URL = "https://raw.githubusercontent.com/tangleroot013/stunning-octo-funicular/main/template_checksums.json"

def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]

def check() -> None:
    local = {p.name: checksum(p) for p in TEMPLATE_DIR.glob("*.j2")}
    try:
        remote = json.loads(urlopen(REF_URL, timeout=5).read())
    except Exception as exc:
        print(f"⚠️  Could not fetch reference: {exc}")
        return
    drift = {k for k in local if local.get(k) != remote.get(k)}
    if drift:
        print(f"⚠️  Template drift detected: {drift}")
    else:
        print("✅ Templates in sync with upstream.")

if __name__ == "__main__":
    check()
