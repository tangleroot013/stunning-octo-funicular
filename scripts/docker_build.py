#!/usr/bin/env python3
"""Build Docker image tagged with current version from settings.json."""

import json
import subprocess
import sys
from pathlib import Path

def build() -> int:
    data = json.loads(Path("settings.json").read_text())
    ver = data["library"]["version"]
    pkg = data["library"]["package_name"]
    tag = f"{pkg}:{ver}"
    
    if not Path("Dockerfile").exists():
        print("❌ Dockerfile missing. Run: python scripts/docker_ready.py")
        return 1
    
    print(f"🔨 Building {tag}...")
    result = subprocess.run(["docker", "build", "-t", tag, "."])
    if result.returncode == 0:
        print(f"✅ Built {tag}")
        subprocess.run(["docker", "tag", tag, f"{pkg}:latest"])
    return result.returncode

if __name__ == "__main__":
    sys.exit(build())
