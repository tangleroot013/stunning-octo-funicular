"""
Interactive scaffolding wizard for Waddler OS Pro.

When hatch.py is run without arguments, this module prompts the user for the
project name, template, base path, coverage threshold, and optional global
template installation before invoking the scaffold engine.
"""

from __future__ import annotations

import re
from typing import Callable, Iterable, Optional, Tuple


TEMPLATE_CHOICES: list[tuple[str, str]] = [
    ("cli", "Command-line tool"),
    ("web", "FastAPI web service"),
    ("lib", "Reusable Python package"),
]

DEFAULT_COVERAGE_THRESHOLD = 85


def _print_banner() -> None:
    print("=" * 50)
    print("Waddler OS Pro - Interactive Scaffolder")
    print("=" * 50)
    print()


def _is_valid_project_name(name: str) -> bool:
    """Project names should be simple, filesystem-safe identifiers."""
    return bool(re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_-]*", name))


def _is_valid_coverage(value: str) -> bool:
    return value.isdigit() and 0 <= int(value) <= 100


def _is_valid_path(path: str) -> bool:
    return bool(path)


def ask(
    question: str,
    default: Optional[str] = None,
    validator: Optional[Callable[[str], bool]] = None,
) -> str:
    """Ask for free-text input, optionally validating and falling back to a default."""
    while True:
        prompt = f"{question}"
        if default is not None:
            prompt = f"{question} [{default}]: "
        print(f"  {prompt}", end="")
        value = input().strip()
        if not value:
            if default is not None:
                return default
            continue
        if validator is not None and not validator(value):
            print(f"    Invalid input for '{question}'. Please try again.")
            continue
        return value


def choose(
    question: str,
    choices: Iterable[Tuple[str, str]],
    default: Optional[str] = None,
) -> str:
    """Show a numbered menu and return the selected key."""
    indexed: list[Tuple[str, str]] = []
    print(f"{question}:")
    for idx, (key, label) in enumerate(choices, start=1):
        indexed.append((key, label))
        print(f"  {idx}. {label}")
    if default:
        print(f"  Press Enter to select default: {default}")

    default_idx = 1
    if default:
        for idx, (key, _) in enumerate(indexed, start=1):
            if key == default:
                default_idx = idx
                break

    while True:
        print(f"  Enter choice (1-{len(indexed)}): ", end="")
        value = input().strip()
        if not value:
            return indexed[default_idx - 1][0]
        if value.isdigit():
            idx = int(value)
            if 1 <= idx <= len(indexed):
                return indexed[idx - 1][0]
        print(f"    Please enter a number between 1 and {len(indexed)}.")


def yes_no(question: str, default: bool = False) -> bool:
    """Ask a yes/no question and return the boolean answer."""
    default_text = "Y/n" if default else "y/N"
    while True:
        print(f"  {question} [{default_text}]: ", end="")
        value = input().strip().lower()
        if not value:
            return default
        if value in {"y", "yes", "true", "1"}:
            return True
        if value in {"n", "no", "false", "0"}:
            return False
        print("    Please answer yes/y or no/n.")


def collect_answers() -> dict:
    """Collect all user choices needed for scaffolding."""
    _print_banner()

    project_name = ask(
        "Project name",
        validator=_is_valid_project_name,
    )

    template = choose(
        "Project template",
        TEMPLATE_CHOICES,
        default="cli",
    )

    base_path = ask(
        "Base directory for the new project",
        default=".",
        validator=_is_valid_path,
    )

    coverage = ask(
        "Coverage threshold (%)",
        default=str(DEFAULT_COVERAGE_THRESHOLD),
        validator=_is_valid_coverage,
    )

    setup_global = yes_no(
        "Install global Git templates and hooks",
        default=False,
    )

    return {
        "project_name": project_name,
        "template": template,
        "base_path": base_path,
        "coverage_threshold": int(coverage),
        "setup_global": setup_global,
    }
