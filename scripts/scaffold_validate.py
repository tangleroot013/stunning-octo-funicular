#!/usr/bin/env python3
"""Validate that generated scaffold projects compile and pass basic checks."""

import subprocess
import tempfile
from pathlib import Path

def validate() -> int:
    if not Path("templates").exists():
        print("ℹ️  No templates/ directory.")
        return 0
    fails = 0
    for tmpl in Path("templates").rglob("*.j2"):
        # Naive: render to temp dir and syntax-check any .py files
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "test.py"
            out.write_text(tmpl.read_text().replace("{{", "").replace("}}", ""))  # strip jinja
            result = subprocess.run([subprocess.sys.executable, "-m", "py_compile", str(out)], capture_output=True)
            if result.returncode != 0:
                print(f"❌ {tmpl}: syntax error in rendered output")
                fails += 1
            else:
                print(f"✅ {tmpl}")
    print(f"\n{'✅ All templates valid' if fails == 0 else f'❌ {fails} template(s) failed'}")
    return fails

if __name__ == "__main__":
    import sys
    sys.exit(validate())
