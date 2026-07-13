#!/usr/bin/env python3
"""Generate commit message from staged diff and commit autonomously."""

import subprocess
import sys
from pathlib import Path

def commit() -> int:
    # Check if anything staged
    staged = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
    if not staged.stdout.strip():
        print("ℹ️  Nothing staged.")
        return 0
    
    # Analyze diff for message
    diff = subprocess.run(["git", "diff", "--cached", "--stat"], capture_output=True, text=True).stdout
    files = staged.stdout.strip().splitlines()
    
    # Determine type
    if all(f.startswith("test") or "test" in f for f in files):
        prefix = "test"
    elif any(f.endswith((".md", ".rst", ".txt")) for f in files):
        prefix = "docs"
    elif "scripts/" in staged.stdout:
        prefix = "chore"
    else:
        prefix = "feat" if any(Path(f).suffix == ".py" for f in files) else "chore"
    
    # Generate message
    scopes = set(Path(f).parts[0] for f in files if Path(f).parts)
    scope = ",".join(sorted(scopes))[:30] if scopes else ""
    desc = f"update {len(files)} file(s)" if len(files) > 1 else Path(files[0]).name
    
    msg = f"{prefix}({scope}): {desc}" if scope else f"{prefix}: {desc}"
    
    print(f"📝 Generated: {msg}")
    confirm = input("Commit? [Y/n]: ").strip().lower()
    if confirm in ("", "y", "yes"):
        subprocess.run(["git", "commit", "-m", msg], check=True)
        print("✅ Committed.")
        return 0
    print("Aborted.")
    return 1

if __name__ == "__main__":
    sys.exit(commit())
