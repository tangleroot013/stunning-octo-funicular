#!/usr/bin/env python3
"""Infer and emit a JSON Schema from the current settings.json structure."""

import json
from pathlib import Path

def infer_schema(obj, required=True):
    if isinstance(obj, dict):
        return {
            "type": "object",
            "properties": {k: infer_schema(v) for k, v in obj.items()},
            "required": list(obj.keys()) if required else []
        }
    elif isinstance(obj, list):
        return {"type": "array", "items": infer_schema(obj[0]) if obj else {}}
    elif isinstance(obj, bool):
        return {"type": "boolean"}
    elif isinstance(obj, int):
        return {"type": "integer"}
    elif isinstance(obj, float):
        return {"type": "number"}
    else:
        return {"type": "string"}

def generate() -> None:
    data = json.loads(Path("settings.json").read_text())
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "stunning-octo-funicular settings",
        **infer_schema(data)
    }
    Path("settings.schema.json").write_text(json.dumps(schema, indent=2))
    print("✅ settings.schema.json generated.")

if __name__ == "__main__":
    generate()
