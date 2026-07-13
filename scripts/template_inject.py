#!/usr/bin/env python3
"""Inject settings.json values into scaffold templates using string.Template."""

import json
import re
from pathlib import Path
from string import Template

def inject() -> None:
    data = json.loads(Path("settings.json").read_text())
    flat = {}
    def flatten(d, prefix=""):
        for k, v in d.items():
            key = f"{prefix}{k}" if not prefix else f"{prefix}_{k}"
            if isinstance(v, dict):
                flatten(v, key)
            else:
                flat[key] = str(v)
    flatten(data)
    
    for tmpl in Path("templates").rglob("*.j2"):
        text = tmpl.read_text()
        result = Template(text).safe_substitute(flat)
        out = Path("scaffold_output") / tmpl.relative_to("templates").with_suffix("")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(result)
        print(f"✅ {out} ({len(re.findall(r'\\$\\w+', result))} unresolved vars)")
    print(f"📦 Injected {len(flat)} keys into {len(list(Path('templates').rglob('*.j2')))} templates.")

if __name__ == "__main__":
    inject()
