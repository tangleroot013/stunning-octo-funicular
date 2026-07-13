#!/usr/bin/env python3
"""Extract Pydantic model schemas from src/ and write openapi fragment."""

import json
import sys
from pathlib import Path

def extract() -> int:
    try:
        import importlib.util
        schemas = {}
        for py in Path("src").rglob("*.py"):
            spec = importlib.util.spec_from_file_location(py.stem, py)
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)
            except Exception:
                continue
            for name in dir(mod):
                obj = getattr(mod, name)
                if hasattr(obj, "model_json_schema"):
                    schemas[f"{py.stem}.{name}"] = obj.model_json_schema()
        Path("schemas.json").write_text(json.dumps(schemas, indent=2))
        print(f"✅ Extracted {len(schemas)} schemas to schemas.json")
        return 0
    except ImportError as e:
        print(f"⚠️  {e}")
        return 0

if __name__ == "__main__":
    sys.exit(extract())
