#!/usr/bin/env python3
"""Add or update license headers in all src/ .py files from a template."""

from pathlib import Path

HEADER = '''\
# Copyright (c) 2026 tangleroot013
# stunning-octo-funicular — Licensed under MIT
#

'''

def inject() -> None:
    updated = 0
    for py in Path("src").rglob("*.py"):
        text = py.read_text()
        if text.startswith("# Copyright"):
            continue  # already has header
        py.write_text(HEADER + text)
        updated += 1
    print(f"✅ Added license header to {updated} file(s).")

if __name__ == "__main__":
    inject()
