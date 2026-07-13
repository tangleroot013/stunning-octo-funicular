#!/usr/bin/env python3
"""Create a PR from current branch with auto-generated title and body."""

import subprocess
import sys
from pathlib import Path

def create() -> int:
    branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    if branch in ("main", "master"):
        print("❌ Cannot PR from main. Create a feature branch.")
        return 1
    
    # Generate title from branch name
    title = branch.replace("-", " ").replace("_", " ").title()
    if branch.startswith("feature/"):
        title = f"feat: {title[8:]}"
    elif branch.startswith("fix/"):
        title = f"fix: {title[4:]}"
    elif branch.startswith("chore/"):
        title = f"chore: {title[6:]}"
    
    # Generate body from commits
    log = subprocess.check_output(
        ["git", "log", "main..HEAD", "--oneline"],
        text=True
    ).strip()
    
    body = f"## Changes\\n\\n" + "\\n".join(f"- {line}" for line in log.splitlines())
    
    # Create PR via gh CLI if available
    result = subprocess.run(
        ["gh", "pr", "create", "--title", title, "--body", body, "--base", "main"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"✅ PR created: {result.stdout.strip()}")
        return 0
    print(f"❌ gh CLI failed: {result.stderr}")
    print(f"   Manual PR title: {title}")
    print(f"   Body preview:\\n{body[:500]}...")
    return 1

if __name__ == "__main__":
    sys.exit(create())
