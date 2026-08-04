"""Utility helpers for the God Mode Scaffolder.

This package exports the core helpers used by the scaffolding CLI and tests.
"""

from .ai_collab import PromptTemplates, WorkspaceFilter, build_llm_payload
from .config_loader import Settings, settings
from .snapshot import build_context_snapshot
from .sync_ignores import SyncIgnoresError, sync_ignore_files
from .wizard import (
    ask,
    choose,
    collect_answers,
    DEFAULT_COVERAGE_THRESHOLD,
    run_wizard,
    yes_no,
)

__all__ = [
    "PromptTemplates",
    "WorkspaceFilter",
    "build_llm_payload",
    "Settings",
    "settings",
    "build_context_snapshot",
    "SyncIgnoresError",
    "sync_ignore_files",
    "ask",
    "choose",
    "collect_answers",
    "DEFAULT_COVERAGE_THRESHOLD",
    "run_wizard",
    "yes_no",
]
