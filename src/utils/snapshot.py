import argparse
import pathlib
from typing import List

from src.utils.config_loader import settings
from src.utils.paths import REPO_ROOT
from src.utils.workspace import load_exclude_patterns


def _iter_project_files(root_dir: pathlib.Path) -> List[pathlib.Path]:
    exclude_globs = load_exclude_patterns()

    files: List[pathlib.Path] = []
    for path in root_dir.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root_dir)
        rel_str = rel.as_posix()
        if any(
            rel_str == pattern or rel_str.startswith(pattern.rstrip("/"))
            for pattern in exclude_globs
        ):
            continue
        files.append(path)
    return sorted(files)


def build_context_snapshot(root_dir: pathlib.Path | None = None) -> pathlib.Path:
    root = pathlib.Path(root_dir or REPO_ROOT).resolve()
    files = _iter_project_files(root)

    max_bytes_per_file = settings.get("ai_collaboration.byte_budget.max_bytes_per_file", 51_200)
    total_payload_limit = settings.get("ai_collaboration.byte_budget.total_payload_limit_bytes", 1_048_576)

    sections: List[str] = [
        "# Project Context Snapshot",
        "",
        "## Overview",
        "",
        f"- Repository: {settings.get('repository.name', root.name)}",
        f"- Assistant: {settings.get('ai_collaboration.target_assistant', 'Claude')}",
        f"- Persona: {settings.get('ai_collaboration.custom_personas.default', 'default')}",
        "",
        "## Files",
        "",
    ]

    used_bytes = 0
    for path in files:
        rel = path.relative_to(root).as_posix()
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            content = ""

        if len(content.encode("utf-8")) > max_bytes_per_file:
            content = content[:max_bytes_per_file] + "\n... [truncated]"

        if used_bytes + len(content.encode("utf-8")) > total_payload_limit:
            break

        used_bytes += len(content.encode("utf-8"))
        sections.extend(
            [
                f"### {rel}",
                "",
                "```text",
                content.rstrip(),
                "```",
                "",
            ]
        )

    output_path = root / "project_snapshot.md"
    output_path.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a compact project context snapshot")
    parser.add_argument("--root", default=".", help="Root directory to scan")
    args = parser.parse_args()
    output_path = build_context_snapshot(pathlib.Path(args.root).resolve())
    print(f"Snapshot written to {output_path}")


if __name__ == "__main__":
    main()
