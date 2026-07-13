#!/usr/bin/env python3
"""Build an optimized AI prompt from current context respecting token budget."""

import json
from pathlib import Path

def build() -> None:
    data = json.loads(Path("settings.json").read_text())
    budget = data.get("ai_collaboration", {}).get("byte_budget", {}).get("max_bytes_per_file", 51200)
    
    context = ["# AI Context Builder\\n"]
    context.append("## Repository Overview")
    context.append(f"- Project: {data['repository']['name']}")
    context.append(f"- Version: {data['library']['version']}")
    context.append(f"- Framework: {data['web']['framework']}\\n")
    
    # Add current task from last commit message
    try:
        import subprocess
        last_msg = subprocess.check_output(["git", "log", "-1", "--pretty=%s"], text=True).strip()
        context.append(f"## Current Task\\n{last_msg}\\n")
    except Exception:
        pass
    
    # Add health snapshot
    health = Path(".health_score")
    if health.exists():
        context.append(f"## Health Score: {health.read_text().strip()}/100\\n")
    
    # Add recent changes
    try:
        import subprocess
        diff = subprocess.check_output(["git", "diff", "--stat", "HEAD~3"], text=True)
        context.append(f"## Recent Changes\\n```\\n{diff}\\n```\\n")
    except Exception:
        pass
    
    output = "\\n".join(context)
    if len(output.encode()) > budget:
        output = output[:budget//2] + "\\n\\n... [truncated to budget] ..."
    
    Path("AI_PROMPT.md").write_text(output)
    print(f"✅ AI_PROMPT.md ({len(output.encode())} bytes, budget: {budget})")

if __name__ == "__main__":
    build()
