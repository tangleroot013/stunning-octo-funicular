"""
Environment dependency checker for the scaffolder.

Performs a pre-flight diagnostic of the host environment before scaffolding
so users get a clear, actionable report instead of a cryptic failure mid-run.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import List, Optional

from src.utils.config_loader import settings


MIN_PYTHON_VERSION = (3, 7)

REQUIRED_TOOLS = {
    "python3": "Python interpreter",
    "pip3": "Python package manager",
    "git": "Version control",
}

OPTIONAL_TOOLS = {
    "ruff": "Fast Python linter",
    "black": "Python formatter",
    "isort": "Import sorter",
    "pytest": "Test runner",
}


@dataclass
class ToolStatus:
    name: str
    label: str
    available: bool
    version: str = ""
    message: str = ""


def _get_version(tool: str) -> str:
    """Return the version string for ``tool`` if it supports --version."""
    try:
        result = subprocess.run(
            [tool, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout.strip().splitlines()[0]
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        pass
    return ""


def _python_meets_minimum() -> bool:
    return sys.version_info >= MIN_PYTHON_VERSION


def _venv_module_available() -> bool:
    try:
        import venv  # noqa: F401
        return True
    except ImportError:
        return False


_UNSET = object()


def _clean_tool_dict(value: object) -> Optional[dict[str, str]]:
    """Return a cleaned string-to-string dict, or None if the input is not a dict."""
    if not isinstance(value, dict):
        return None
    return {
        k: v
        for k, v in value.items()
        if isinstance(k, str) and isinstance(v, str)
    }


def _load_tool_lists() -> tuple[dict[str, str], dict[str, str]]:
    """Load required/optional tool lists from settings when present.

    A missing key falls back to the built-in defaults. An explicit empty dict
    means "no additional tools beyond python/venv", which is honored.
    """
    preflight = settings.get("developer_environment.preflight_checks", {})
    if not isinstance(preflight, dict):
        return REQUIRED_TOOLS, OPTIONAL_TOOLS

    raw_required = preflight.get("required", _UNSET)
    raw_optional = preflight.get("optional", _UNSET)

    required = (
        _clean_tool_dict(raw_required)
        if raw_required is not _UNSET
        else REQUIRED_TOOLS
    )
    optional = (
        _clean_tool_dict(raw_optional)
        if raw_optional is not _UNSET
        else OPTIONAL_TOOLS
    )

    return (
        required if required is not None else REQUIRED_TOOLS,
        optional if optional is not None else OPTIONAL_TOOLS,
    )


def check_environment(include_optional: bool = True) -> tuple[bool, List[ToolStatus]]:
    """Run the environment pre-flight check.

    Args:
        include_optional: When False, only required tools are checked. Useful
            for a lightweight pre-scaffold smoke test.

    Returns a (pass, statuses) tuple. ``pass`` is True only when the minimum
    Python version is satisfied and all required tools are found.
    """
    required, optional = _load_tool_lists()
    statuses: List[ToolStatus] = []
    passed = _python_meets_minimum()

    # Python is always checked first.
    statuses.append(
        ToolStatus(
            name="python3",
            label="Python interpreter",
            available=passed,
            version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            message=(
                ""
                if passed
                else f"Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+ is required"
            ),
        )
    )

    # venv is a special check because it's a standard library module.
    venv_ok = _venv_module_available()
    statuses.append(
        ToolStatus(
            name="venv",
            label="Python venv module",
            available=venv_ok,
            message="" if venv_ok else "python3-venv package may not be installed",
        )
    )
    passed = passed and venv_ok

    skip_in_loop = {"python3", "python", "venv"}
    for tool, label in required.items():
        if tool in skip_in_loop:
            continue
        path = shutil.which(tool)
        version = _get_version(tool) if path else ""
        available = path is not None
        statuses.append(
            ToolStatus(
                name=tool,
                label=label,
                available=available,
                version=version,
                message="" if available else f"{tool} is not installed or not in PATH",
            )
        )
        passed = passed and available

    if include_optional:
        for tool, label in optional.items():
            path = shutil.which(tool)
            version = _get_version(tool) if path else ""
            statuses.append(
                ToolStatus(
                    name=tool,
                    label=label,
                    available=path is not None,
                    version=version,
                    message=(
                        ""
                        if path
                        else f"{tool} not found; scaffolding will still work, but pre-commit hooks may be skipped"
                    ),
                )
            )

    return passed, statuses


def format_report(statuses: List[ToolStatus], passed: bool) -> str:
    """Return a human-readable pre-flight report."""
    lines = ["Environment Pre-flight Check", "=" * 40]
    for status in statuses:
        symbol = "✓" if status.available else "✗"
        version = f" ({status.version})" if status.version else ""
        lines.append(f"{symbol} {status.label}: {status.name}{version}")
        if status.message:
            lines.append(f"    {status.message}")

    lines.append("=" * 40)
    lines.append("All good" if passed else "Some requirements are missing")
    return "\n".join(lines)


def main() -> int:
    passed, statuses = check_environment()
    print(format_report(statuses, passed))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
