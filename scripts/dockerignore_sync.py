#!/usr/bin/env python3
"""Generate .dockerignore from .gitignore + Docker-specific additions."""

from pathlib import Path

DOCKER_EXTRA = [
    ".git",
    ".env",
    ".env.*",
    "Dockerfile",
    "docker-compose.yml",
    ".dockerignore",
    "Makefile",
    "scripts/",
    "tests/",
    "docs/",
    "*.md",
    ".github/",
]

def sync() -> None:
    gitignore = Path(".gitignore")
    lines = ["# Auto-generated from .gitignore + Docker extras\\n"]
    if gitignore.exists():
        lines.append(gitignore.read_text().strip())
    lines.extend(["\\n# Docker-specific"] + DOCKER_EXTRA)
    Path(".dockerignore").write_text("\\n".join(lines) + "\\n")
    print("✅ .dockerignore synced.")

if __name__ == "__main__":
    sync()
