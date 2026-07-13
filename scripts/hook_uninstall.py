#!/usr/bin/env python3
"""Remove all git hooks installed by this workspace."""

import shutil
from pathlib import Path

def uninstall() -> None:
    hooks_dir = Path(".git/hooks")
    if not hooks_dir.exists():
        print("ℹ️  No .git/hooks directory.")
        return
    
    installed = []
    for hook in hooks_dir.iterdir():
        if hook.is_file() and not hook.name.endswith(".sample"):
            # Check if it's one of ours
            content = hook.read_text(errors="ignore")
            if "scripts/" in content or "stunning-octo-funicular" in content:
                hook.unlink()
                installed.append(hook.name)
    
    if installed:
        print(f"🗑️  Removed {len(installed)} hook(s): {', '.join(installed)}")
    else:
        print("ℹ️  No workspace hooks found.")

if __name__ == "__main__":
    uninstall()
