import subprocess
from pathlib import Path
from typing import List

from src.plugins.interface import PluginProtocol


class MyWebApiAdapter:
    name = "my-web-api"
    description = "Adapter wrapper for the my-web-api repository"

    def run(self, args: List[str]) -> int:
        repo = Path(r"/home/tangleroot013/github_projects/my-web-api")
        if not repo.exists():
            print("✗ my-web-api repository not found at", repo)
            return 2
        if "--exec" in args:
            # Example: run tests if pytest exists, otherwise list files
            if (repo / 'pyproject.toml').exists() or (repo / 'requirements.txt').exists():
                cmd = ["/usr/bin/env", "bash", "-lc", "echo Running tests; pytest -q || true"]
            else:
                cmd = ["/usr/bin/env", "bash", "-lc", "ls -la"]
            print("Running adapter command in {}: {}".format(repo, ' '.join(cmd)))
            return subprocess.run(cmd, cwd=str(repo)).returncode
        else:
            print("[dry-run] would run my-web-api adapter against {}".format(repo))
            print("Use --exec to execute a simple adapter command")
            return 0


adapter = MyWebApiAdapter()
