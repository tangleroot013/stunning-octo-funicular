"""
Interactive scaffolding wizard for Waddler OS Pro.
"""

from __future__ import annotations

import re
import sys
import pathlib
from typing import Callable, Iterable, Optional, Tuple
from dataclasses import dataclass

__all__ = [
    "ask",
    "choose",
    "yes_no",
    "collect_answers",
    "run_wizard",
    "DEFAULT_COVERAGE_THRESHOLD",
    "TEMPLATE_CHOICES",
    "is_valid_project_name",
    "is_valid_coverage",
]


class Color:
    """ANSI color codes for terminal styling."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    CYAN = "\033[36m"


@dataclass(frozen=True)
class TemplateChoice:
    key: str
    label: str


TEMPLATE_CHOICES: tuple[TemplateChoice, ...] = (
    TemplateChoice("cli", "Command-line tool"),
    TemplateChoice("web", "FastAPI web service"),
    TemplateChoice("lib", "Reusable Python package"),
)

DEFAULT_COVERAGE_THRESHOLD = 85


def _print_banner() -> None:
    width = 50
    print(f"{Color.CYAN}{'=' * width}{Color.RESET}")
    print(f"{Color.BOLD}{Color.GREEN}Waddler OS Pro - Interactive Scaffolder 🚀{Color.RESET}")
    print(f"{Color.CYAN}{'=' * width}{Color.RESET}")
    print()


def is_valid_project_name(name: str) -> bool:
    """Return True if *name* is a simple, filesystem-safe identifier."""
    return bool(re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_-]*", name))


def is_valid_coverage(value: str) -> bool:
    """Return True if *value* is an integer between 0 and 100."""
    return value.isdigit() and 0 <= int(value) <= 100


def _is_valid_path(path: str) -> bool:
    return bool(path.strip())


def _as_str(value: object) -> Optional[str]:
    return str(value) if value is not None else None


def ask(
    question: str,
    default: Optional[str] = None,
    validator: Optional[Callable[[str], bool]] = None,
    validation_error_msg: Optional[str] = None,
) -> str:
    """Ask for free-text input, optionally validating and falling back to a default."""
    default = _as_str(default)
    while True:
        prompt = f"{question}: "
        if default is not None:
            prompt = f"{question} [{default}]: "
        print(f"  {prompt}", end="")
        try:
            value = input().strip()
        except EOFError:
            value = ""
        if not value:
            if default is not None:
                return default
            continue
        if validator is not None and not validator(value):
            error_msg = validation_error_msg or f"Invalid input for '{question}'."
            print(f"    {Color.YELLOW}{error_msg} Please try again.{Color.RESET}")
            continue
        return value


def choose(
    question: str,
    choices: Iterable[TemplateChoice],
    default: Optional[str] = None,
) -> str:
    """Show a numbered menu and return the selected key."""
    indexed: list[TemplateChoice] = list(choices)
    print(f"{question}:")
    for idx, choice in enumerate(indexed, start=1):
        print(f"  {idx}. {choice.key.upper()} - {choice.label}")
    if default:
        print(f"  Press Enter to select default: {default}")

    default_idx = 1
    if default:
        for idx, choice in enumerate(indexed, start=1):
            if choice.key == default:
                default_idx = idx
                break

    while True:
        print(f"  Enter choice (1-{len(indexed)}): ", end="")
        try:
            value = input().strip()
        except EOFError:
            value = ""
        if not value:
            return indexed[default_idx - 1].key
        if value.isdigit():
            idx = int(value)
            if 1 <= idx <= len(indexed):
                return indexed[idx - 1].key
        print(f"    {Color.YELLOW}Please enter a number between 1 and {len(indexed)}.{Color.RESET}")


def yes_no(question: str, default: bool = False) -> bool:
    """Ask a yes/no question and return the boolean answer."""
    default_text = "Y/n" if default else "y/N"
    while True:
        print(f"  {question} [{default_text}]: ", end="")
        try:
            value = input().strip().lower()
        except EOFError:
            value = ""
        if not value:
            return default
        if value in {"y", "yes", "true", "1"}:
            return True
        if value in {"n", "no", "false", "0"}:
            return False
        print(f"    {Color.YELLOW}Please answer yes/y or no/n.{Color.RESET}")


def collect_answers(defaults: Optional[dict] = None) -> dict:
    """Collect all user choices needed for scaffolding."""
    defaults = defaults or {}
    try:
        _print_banner()

        project_name = ask(
            "Project name",
            default=defaults.get("project_name"),
            validator=is_valid_project_name,
            validation_error_msg="Project name must start with a letter and contain only letters, numbers, hyphens, or underscores.",
        )

        template = choose(
            "Project template",
            TEMPLATE_CHOICES,
            default=defaults.get("template", "cli"),
        )

        base_path_raw = ask(
            "Base directory for the new project",
            default=defaults.get("base_path", "."),
            validator=_is_valid_path,
        )
        
        base_path = str(pathlib.Path(base_path_raw).expanduser().resolve())

        coverage_default = defaults.get("coverage_threshold", DEFAULT_COVERAGE_THRESHOLD)
        if not isinstance(coverage_default, int) or not (0 <= coverage_default <= 100):
            coverage_default = DEFAULT_COVERAGE_THRESHOLD
        coverage = ask(
            "Coverage threshold (%)",
            default=str(coverage_default),
            validator=is_valid_coverage,
            validation_error_msg="Coverage threshold must be an integer between 0 and 100.",
        )

        setup_global = yes_no(
            "Install global Git templates and hooks",
            default=bool(defaults.get("setup_global", False)),
        )

        return {
            "project_name": project_name,
            "template": template,
            "base_path": base_path,
            "coverage_threshold": int(coverage),
            "setup_global": setup_global,
        }
    except KeyboardInterrupt:
        print(f"\n\n  {Color.RED}{Color.BOLD}✕ Scaffolding aborted by user. Goodbye!{Color.RESET} 👋")
        sys.exit(130)


def run_wizard(defaults: Optional[dict] = None) -> dict:
    """Entry-point wrapper that always returns a dict (never None)."""
    return collect_answers(defaults)

