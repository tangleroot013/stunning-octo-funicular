import subprocess
from pathlib import Path
from typing import List

from src.plugins.interface import PluginProtocol


class GodStackAdapter:
    name = "god_stack"
    description = "Adapter wrapper for the god_stack repository"

    def run(self, args: List[str]) -> int:
        repo = Path('/home/tangleroot013/github_projects/god_stack')
        if not repo.exists():
            print("✗ god_stack repository not found at", repo)
            return 2
        # If --exec provided, run a helpful command; otherwise dry-run message
        if "--exec" in args:
            cmd = ["/usr/bin/env", "bash", "-lc", "ls -la"]
            print(f"Running adapter command in {repo}: {' '.join(cmd)}")
            return subprocess.run(cmd, cwd=str(repo)).returncode
        else:
            print(f"[dry-run] would run god_stack adapter against {repo}")
            print("Use --exec to execute a simple adapter command")
            return 0


adapter = GodStackAdapter()
