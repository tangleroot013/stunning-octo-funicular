#!/usr/bin/env python3
"""Flag inconsistent emoji usage in commit messages and source comments."""

import re
import subprocess
import sys
from pathlib import Path

EMOJI_SET = {"✅", "❌", "⚠️", "🚨", "🔥", "💥", "🐛", "✨", "♻️", "📦", "🔒", "🚀", "🎯", "📊", "🗑️", "🔧", "📚", "🏷️", "💡", "🔍"}
PATTERN = re.compile(r"[\\U0001F300-\\U0001F9FF]")

def lint() -> int:
    hits = 0
    # Check commits
    log = subprocess.check_output(["git", "log", "-20", "--pretty=%s"], text=True).splitlines()
    for msg in log:
        emojis = set(PATTERN.findall(msg))
        unknown = emojis - EMOJI_SET
        if unknown:
            print(f"⚠️  Unknown emoji in commit: {msg[:50]}... ({unknown})")
            hits += 1
    
    # Check source
    for py in Path("src").rglob("*.py"):
        text = py.read_text()
        for i, line in enumerate(text.splitlines(), 1):
            emojis = set(PATTERN.findall(line))
            unknown = emojis - EMOJI_SET
            if unknown and not line.strip().startswith("#"):
                print(f"⚠️  {py}:{i} emoji in code (not comment): {line.strip()[:60]}")
                hits += 1
    
    if hits:
        print(f"\n❌ {hits} emoji violation(s). Standardize or move to comments.")
        return 1
    print("✅ Emoji usage consistent.")
    return 0

if __name__ == "__main__":
    sys.exit(lint())
