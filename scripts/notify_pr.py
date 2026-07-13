#!/usr/bin/env python3
"""Open browser to create PR and copy branch name to clipboard."""

import subprocess
import webbrowser
from pathlib import Path

def open_pr() -> None:
    branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    remote = subprocess.check_output(["git", "remote", "get-url", "origin"], text=True).strip()
    if "github.com" in remote:
        owner_repo = remote.replace("git@github.com:", "").replace("https://github.com/", "").replace(".git", "")
        url = f"https://github.com/{owner_repo}/compare/main...{branch}?expand=1"
        webbrowser.open(url)
        print(f"🌐 Opened PR page for {branch}")
        # Try clipboard
        for copier in ("pbcopy", "xclip", "wl-copy"):
            if subprocess.run(["which", copier], capture_output=True).returncode == 0:
                proc = subprocess.Popen([copier], stdin=subprocess.PIPE, text=True)
                proc.communicate(branch)
                print("📋 Branch name copied to clipboard.")
                break

if __name__ == "__main__":
    open_pr()
