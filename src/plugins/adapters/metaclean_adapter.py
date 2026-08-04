import subprocess
from pathlib import Path
from typing import List

from src.plugins.interface import PluginProtocol


class MetaCleanAdapter:
    name = "metaclean"
    description = "Adapter wrapper for the metaclean repository"

    def run(self, args: List[str]) -> int:
        repo = Path('/home/tangleroot013/github_projects/metaclean')
        if not repo.exists():
            print("✗ metaclean repository not found at", repo)
            return 2
        if "--exec" in args:
            cmd = ["/usr/bin/env", "bash", "-lc", "echo metaclean adapter running; ls -1"]
            print(f"Running adapter command in {repo}: {' '.join(cmd)}")
            return subprocess.run(cmd, cwd=str(repo)).returncode
        else:
            print(f"[dry-run] would run metaclean adapter against {repo}")
            print("Use --exec to execute a simple adapter command")
            return 0


adapter = MetaCleanAdapter()
