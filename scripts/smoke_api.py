#!/usr/bin/env python3
"""Smoke-test the local FastAPI instance using settings.json config."""

import json
import sys
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

def smoke() -> int:
    cfg = json.loads(Path("settings.json").read_text())["web"]["server"]
    host, port = cfg["host"], cfg["port"]
    url = f"http://{host}:{port}/health"
    try:
        resp = urlopen(url, timeout=3)
        print(f"✅ {url} → {resp.status}")
        return 0
    except URLError as exc:
        print(f"❌ {url} unreachable: {exc.reason}")
        return 1

if __name__ == "__main__":
    sys.exit(smoke())
