#!/usr/bin/env python3
"""Check GitHub Actions workflow files for outdated action references (no version pin)."""

import re
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for wf in Path(".github/workflows").rglob("*.yml"):
        text = wf.read_text()
        uses = re.findall(r"uses:\\s*(.+)", text)
        for ref in uses:
            ref = ref.strip()
            if "@" not in ref or ref.endswith("@main") or ref.endswith("@master"):
                print(f"⚠️  {wf}: unpinned or mutable ref '{ref}'")
                hits += 1
            elif re.search(r"@v?\\d+$", ref):
                print(f"⚠️  {wf}: major-only pin '{ref}' (consider @v4.1.2)")
                hits += 1
            else:
                print(f"✅ {wf}: {ref}")
    if hits:
        print(f"\\n❌ {hits} mutable action reference(s). Pin to SHA or full version.")
        return 1
    print("✅ All action references are immutable.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
