#!/usr/bin/env python3
"""Generate a shields.io badge for health score and inject into README.md."""

import re
from pathlib import Path

def update() -> None:
    score = Path(".health_score").read_text().strip() if Path(".health_score").exists() else "0"
    color = "brightgreen" if int(score) >= 80 else "yellow" if int(score) >= 60 else "red"
    badge = f"![health](https://img.shields.io/badge/health-{score}%25-{color})"
    
    readme = Path("README.md")
    if not readme.exists():
        readme.write_text(f"{badge}\\n\\n# stunning-octo-funicular\\n")
        print("✅ README.md created with badge.")
        return
    
    text = readme.read_text()
    pattern = re.compile(r"!\\[health\\]\\([^)]+\\)")
    if pattern.search(text):
        text = pattern.sub(badge, text)
    else:
        text = badge + "\\n\\n" + text
    readme.write_text(text)
    print(f"✅ Health badge updated: {score}%")

if __name__ == "__main__":
    update()
