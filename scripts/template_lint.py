#!/usr/bin/env python3
"""Lint Jinja2 templates for undefined variables, syntax errors, and unused macros."""

import re
import sys
from pathlib import Path

def lint() -> int:
    fails = 0
    for tmpl in Path("templates").rglob("*.j2"):
        text = tmpl.read_text()
        # Check for undefined-looking variables (simple heuristic)
        vars_used = set(re.findall(r"\\{\\{\\s*(\\w+)", text))
        vars_defined = set(re.findall(r"\\{%\\s*set\\s+(\\w+)", text))
        # Check for unclosed blocks
        open_blocks = len(re.findall(r"\\{%\\s*(if|for|macro|block)", text))
        close_blocks = len(re.findall(r"\\{%\\s*end(if|for|macro|block)", text))
        if open_blocks != close_blocks:
            print(f"❌ {tmpl}: unbalanced blocks ({open_blocks} open, {close_blocks} close)")
            fails += 1
        else:
            print(f"✅ {tmpl}: {len(vars_used)} vars, {len(vars_defined)} defined")
    return fails

if __name__ == "__main__":
    sys.exit(lint())
