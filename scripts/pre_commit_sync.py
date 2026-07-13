#!/usr/bin/env python3
"""Generate .pre-commit-config.yaml from settings.json hooks list."""

import json
from pathlib import Path

HOOK_MAP = {
    "detect-secrets": {"repo": "https://github.com/Yelp/detect-secrets", "rev": "v1.4.0", "id": "detect-secrets"},
    "py_compile": {"repo": "https://github.com/pre-commit/pre-commit-hooks", "rev": "v4.4.0", "id": "check-ast"},
    "ruff": {"repo": "https://github.com/astral-sh/ruff-pre-commit", "rev": "v0.1.0", "id": "ruff"},
    "black": {"repo": "https://github.com/psf/black", "rev": "23.9.1", "id": "black"},
    "isort": {"repo": "https://github.com/PyCQA/isort", "rev": "5.12.0", "id": "isort"},
    "trailing-whitespace": {"repo": "https://github.com/pre-commit/pre-commit-hooks", "rev": "v4.4.0", "id": "trailing-whitespace"},
}

def sync() -> None:
    data = json.loads(Path("settings.json").read_text())
    hooks = data["ci"]["pre_commit"]["hooks"]
    entries = []
    for h in hooks:
        mapped = HOOK_MAP.get(h)
        if mapped:
            entries.append(f"  - repo: {mapped['repo']}\n    rev: {mapped['rev']}\n    hooks:\n      - id: {mapped['id']}")
    yaml = "# Auto-generated from settings.json\nrepos:\n" + "\n".join(entries)
    Path(".pre-commit-config.yaml").write_text(yaml + "\n")
    print("✅ .pre-commit-config.yaml synced.")

if __name__ == "__main__":
    sync()
