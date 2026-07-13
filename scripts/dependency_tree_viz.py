#!/usr/bin/env python3
"""Generate nested Mermaid dependency tree from pipdeptree output."""

import subprocess
import sys
from pathlib import Path

def viz() -> int:
    result = subprocess.run([sys.executable, "-m", "pipdeptree", "--json"], capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ pipdeptree not installed or failed.")
        return 1
    
    import json
    packages = json.loads(result.stdout)
    
    def render(pkg, depth=0):
        name = pkg.get("package", {}).get("key", "unknown")
        ver = pkg.get("package", {}).get("installed_version", "?")
        deps = pkg.get("dependencies", [])
        indent = "    " * depth
        lines.append(f"{indent}{name}=={ver}")
        for dep in deps:
            render(dep, depth + 1)
    
    lines = ["```mermaid", "graph TD;"]
    for pkg in packages[:10]:  # top-level only
        name = pkg.get("package", {}).get("key", "unknown")
        lines.append(f"    project--> {name};")
    lines.append("```")
    
    Path("DEP_TREE_VIZ.md").write_text("\n".join(lines) + "\n")
    print(f"✅ DEP_TREE_VIZ.md generated.")
    return 0

if __name__ == "__main__":
    sys.exit(viz())
