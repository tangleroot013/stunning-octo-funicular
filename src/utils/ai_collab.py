import fnmatch
import pathlib
from typing import Any, Dict, List

from src.utils.config_loader import settings
from src.utils.sync_ignores import DEFAULT_CLAUDEIGNORE_PATTERNS


def _validate_patterns(patterns: Any) -> List[str]:
    if patterns is None:
        return []
    if not isinstance(patterns, list):
        return []
    cleaned: List[str] = []
    for pattern in patterns:
        if not isinstance(pattern, str):
            continue
        pattern = pattern.strip()
        if pattern:
            cleaned.append(pattern)
    return cleaned


class PromptTemplates:
    """Load prompt templates from settings.json."""

    _templates: Dict[str, str] = {}

    @classmethod
    def load(cls) -> None:
        raw = settings.get("ai_collaboration.templates", {})
        if not isinstance(raw, dict):
            raise RuntimeError("ai_collaboration.templates must be a mapping")
        cls._templates = raw

    @classmethod
    def get(cls, name: str, default: str = "") -> str:
        if not cls._templates:
            cls.load()
        return cls._templates.get(name, default)


class WorkspaceFilter:
    """Collect a compact, settings-driven set of files for LLM context."""

    _repo_root: pathlib.Path = pathlib.Path(__file__).resolve().parents[2]

    @classmethod
    def _load_rules(cls) -> Dict[str, Any]:
        base_key = "ai_collaboration.directory_scanning_protection"
        workspace_patterns = settings.get("workspace.ignore_patterns", {})
        patterns = None
        explicit_override = False

        if isinstance(workspace_patterns, dict) and "claudeignore" in workspace_patterns:
            raw_claude_patterns = workspace_patterns["claudeignore"]
            if isinstance(raw_claude_patterns, list):
                patterns = _validate_patterns(raw_claude_patterns)
                if patterns:
                    explicit_override = True
                else:
                    patterns = None
            else:
                patterns = []
                explicit_override = True

        if patterns is None:
            ai_patterns = settings.get(f"{base_key}.exclude_globs", None)
            if ai_patterns is not None:
                if isinstance(ai_patterns, list):
                    patterns = _validate_patterns(ai_patterns)
                    if patterns:
                        explicit_override = True
                    else:
                        patterns = None
                else:
                    patterns = []
                    explicit_override = True

        if patterns is None or (not patterns and not explicit_override):
            patterns = DEFAULT_CLAUDEIGNORE_PATTERNS.copy()

        rules = {
            "exclude_patterns": patterns,
            "max_total_bytes": settings.get(f"{base_key}.max_bytes", 400_000),
        }
        return rules

    @classmethod
    def _is_excluded(cls, rel_path: pathlib.Path, patterns: List[str]) -> bool:
        path_str = str(rel_path.as_posix())
        for pat in patterns:
            if pat.endswith("/"):
                if path_str.startswith(pat):
                    return True
                continue
            if pat.endswith("/**"):
                prefix = pat[:-3]
                if path_str == prefix or path_str.startswith(prefix + "/"):
                    return True
                continue
            if fnmatch.fnmatch(path_str, pat):
                return True
        return False

    @classmethod
    def collect_files(cls) -> List[pathlib.Path]:
        rules = cls._load_rules()
        excluded = rules["exclude_patterns"]
        budget = rules["max_total_bytes"]

        selected: List[pathlib.Path] = []
        used_bytes = 0

        for file_path in sorted(cls._repo_root.rglob("*")):
            if file_path.is_dir():
                continue

            rel = file_path.relative_to(cls._repo_root)
            if cls._is_excluded(rel, excluded):
                continue

            size = file_path.stat().st_size
            if size > budget:
                continue
            if used_bytes + size > budget:
                continue

            selected.append(file_path)
            used_bytes += size

        return selected


def build_llm_payload() -> Dict[str, Any]:
    """Return a ready-to-send payload for AI-assisted scaffolding."""
    mode = settings.get("ai_collaboration.token_efficiency_mode", "strict")
    if mode not in {"strict", "relaxed"}:
        mode = "strict"

    system_prompt = PromptTemplates.get(
        "system",
        "You are a helpful AI assistant.",
    )
    user_prompt = PromptTemplates.get(
        "task",
        "Please answer the following request.",
    )

    if mode == "relaxed":
        patterns = settings.get("ai_collaboration.directory_scanning_protection.exclude_globs", [])
        files = [
            p
            for p in pathlib.Path.cwd().rglob("*")
            if p.is_file() and not any(fnmatch.fnmatch(str(p.relative_to(pathlib.Path.cwd()).as_posix()), pat) for pat in patterns)
        ]
    else:
        files = WorkspaceFilter.collect_files()

    file_entries = []
    for p in files:
        try:
            content = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = ""
        file_entries.append(
            {
                "path": str(p.relative_to(WorkspaceFilter._repo_root)),
                "content": content,
            }
        )

    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "files": file_entries,
    }
