#!/usr/bin/env python3
"""Prune merged branches while protecting main/release lines."""

import subprocess
from pathlib import Path

PROTECTED = {"main", "master", "release/*", "hotfix/*"}

def is_protected(name: str) -> bool:
    return any(name == p or name.startswith(p.rstrip("*")) for p in PROTECTED)

def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()

def cleanup() -> None:
    run(["git", "fetch", "--prune"])
    merged = run(["git", "branch", "--merged", "main", "--format=%(refname:short)"])
    for branch in merged.splitlines():
        if branch and not is_protected(branch):
            run(["git", "branch", "-d", branch])
            print(f"🗑️  Deleted local branch: {branch}")
    print("✅ Cleanup complete.")

if __name__ == "__main__":
    if not Path(".git").exists():
        raise SystemExit("Not a git repository.")
    cleanup()
