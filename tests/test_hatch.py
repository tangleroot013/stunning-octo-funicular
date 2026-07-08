from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import hatch


def test_scaffold_generates_ci_and_hook_templates(tmp_path, monkeypatch):
    monkeypatch.setattr(hatch, "init_git_repo", lambda project_path: None)

    project_dir = hatch.scaffold("demo-app", str(tmp_path), "cli")

    assert project_dir == tmp_path / "demo-app"
    assert (project_dir / ".claudeignore").exists()
    assert (project_dir / ".gitignore").exists()
    assert (project_dir / "requirements.txt").exists()

    workflow = (project_dir / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "lint-and-format" in workflow
    assert "ruff check --fix" in workflow
    assert "pytest --cov ." in workflow

    hook = (project_dir / ".git" / "hooks" / "pre-commit").read_text(encoding="utf-8")
    assert "QUACK! Secret detected in staged changes!" in hook
    assert "ruff check --fix" in hook
    assert "black --check" in hook
    assert "isort --check-only" in hook
