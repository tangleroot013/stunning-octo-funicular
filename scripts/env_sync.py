#!/usr/bin/env python3
"""Generate .env.example from CI environments in settings.json."""

import json
from pathlib import Path

def sync() -> None:
    data = json.loads(Path("settings.json").read_text())
    envs = data["ci"]["environments"]
    lines = ["# Auto-generated from settings.json\n"]
    for name, vars in envs.items():
        lines.append(f"\n# --- {name} ---")
        for k, v in vars.items():
            lines.append(f"{k}={v}")
    Path(".env.example").write_text("\n".join(lines) + "\n")
    print("✅ .env.example synced from settings.json.")

if __name__ == "__main__":
    sync()
