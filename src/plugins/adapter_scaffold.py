"""Simple adapter scaffolder to generate adapter modules for local repos.

Usage from code:
    from src.plugins.adapter_scaffold import scaffold_adapter
    scaffold_adapter('my-repo', Path('/path/to/my-repo'))

The generated adapter follows the pattern used by other example adapters: it checks
for repo existence, prints dry-run instructions by default, and performs a safe
example command when run with --exec.
"""
from pathlib import Path

TEMPLATE = '''import subprocess
from pathlib import Path
from typing import List

from src.plugins.interface import PluginProtocol


class {class_name}:
    name = "{name}"
    description = "Adapter wrapper for the {name} repository"

    def run(self, args: List[str]) -> int:
        repo = Path(r"{repo_path}")
        if not repo.exists():
            print("✗ {name} repository not found at", repo)
            return 2
        if "--exec" in args:
            # Example: run tests if pytest exists, otherwise list files
            if (repo / 'pyproject.toml').exists() or (repo / 'requirements.txt').exists():
                cmd = ["/usr/bin/env", "bash", "-lc", "echo Running tests; pytest -q || true"]
            else:
                cmd = ["/usr/bin/env", "bash", "-lc", "ls -la"]
            print("Running adapter command in {{}}: {{}}".format(repo, ' '.join(cmd)))
            return subprocess.run(cmd, cwd=str(repo)).returncode
        else:
            print("[dry-run] would run {name} adapter against {{}}".format(repo))
            print("Use --exec to execute a simple adapter command")
            return 0


adapter = {class_name}()
'''


def scaffold_adapter(name: str, repo_path: Path, adapters_dir: Path) -> Path:
    """Create an adapter module file for the given repo name and path.

    Returns the path to the created module.
    """
    safe_name = name.replace('-', '_')
    class_name = ''.join(x.capitalize() for x in safe_name.split('_')) + 'Adapter'
    target = adapters_dir / f"{safe_name}_adapter.py"
    content = TEMPLATE.format(class_name=class_name, name=name, repo_path=str(repo_path))
    target.write_text(content, encoding='utf-8')
    return target
