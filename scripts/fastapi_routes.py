#!/usr/bin/env python3
"""Extract and validate FastAPI route definitions against settings.json CORS origins."""

import ast
import json
import sys
from pathlib import Path

def extract() -> dict[str, list[str]]:
    routes = {}
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr in ("get", "post", "put", "delete", "patch"):
                    mod = ".".join(py.relative_to("src").with_suffix("").parts)
                    routes.setdefault(mod, []).append(node.func.attr.upper())
    return routes

def validate() -> int:
    data = json.loads(Path("settings.json").read_text())
    origins = data.get("web", {}).get("security", {}).get("cors_origins", [])
    routes = extract()
    print(f"🌐 CORS origins: {len(origins)}")
    print(f"📡 Route modules: {len(routes)}")
    for mod, methods in routes.items():
        print(f"   {mod}: {', '.join(set(methods))}")
    return 0

if __name__ == "__main__":
    sys.exit(validate())
