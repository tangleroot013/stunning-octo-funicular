#!/usr/bin/env python3
"""Validate latest commit message follows conventional commit spec."""

import re
import subprocess
import sys

PATTERN = re.compile(r"^(feat|fix|chore|docs|refactor|test|ci|build)(\(.+\))?!?: .+")

def lint() -> int:
    msg = subprocess.check_output(["git", "log", "-1", "--pretty=%B"], text=True).strip()
    if PATTERN.match(msg.splitlines()[0]):
        print("✅ Commit message follows convention.")
        return 0
    print("❌ Commit message must follow: type(scope)?: description")
    print(f"   Got: {msg.splitlines()[0][:60]}...")
    return 1

if __name__ == "__main__":
    sys.exit(lint())
