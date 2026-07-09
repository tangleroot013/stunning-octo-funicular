# Architecture

This document describes how the God Mode Scaffolder fits together and how each module contributes to project generation.

## Overview

The scaffolder is a single-file CLI (`hatch.py`) plus a set of small utilities in `src/utils/`. It is intentionally dependency-light so it can run on a base Python install.

```text
User
  |
  v
hatch.py::main()
  |-- version
  |-- sync-ignores
  |-- setup-global
  |-- check-env       (in PR #2)
  |-- run_wizard
  |-- scaffold
       |
       v
       Generated project directory
```

## Configuration

`src/utils/config_loader.py` loads `settings.json` once into a singleton `Settings` instance. Callers use dotted keys and a default value:

```python
settings.get("ci.pre_commit.hooks", [])
```

This lets `settings.json` drive ignore patterns, CI hooks, byte budgets, and AI personas without hard-coding them in `hatch.py`.

## CLI entry point

`hatch.py::main()` uses `argparse` to handle:

- positional `project_name`
- `--path`, `--template`, `--coverage-threshold`
- `--setup-global`
- `--sync-ignores` with optional `--dry-run`
- `--version`
- `--check-env` (in PR #2)

If no `project_name` is supplied, `run_wizard()` is called. CLI flags are forwarded as defaults to the wizard where appropriate.

## Wizard

`src/utils/wizard.py` collects user input through a small set of helpers:

- `ask()` — free-text input with optional validation
- `choose()` — numbered menu
- `yes_no()` — yes/no prompt
- `collect_answers()` — orchestrates all prompts and returns a result dictionary

Defaults passed from the CLI pre-fill wizard answers where they make sense.

## Scaffold engine

`scaffold(project_name, base_path, template, coverage_threshold=85)` does the actual work:

1. Creates directories from the selected `TEMPLATES` entry.
2. Calls `sync_ignore_files()` to write `.claudeignore` and `.gitignore`.
3. Writes `README.md`, `requirements.txt`, and the CI `pipeline.yml`.
4. Renders template files with `render_template()`.
5. Initializes Git and installs local pre-commit hooks and a commit message template.

The `pipeline.yml` uses the `coverage_threshold` argument so generated projects enforce the chosen minimum coverage.

## Ignore synchronization

`src/utils/sync_ignores.py` reads `workspace.ignore_patterns.claudeignore` and `workspace.ignore_patterns.gitignore` from `settings.json`. It writes both files to the target directory. `--dry-run` reports what would change without writing.

## Snapshot generator

`src/utils/snapshot.py` walks the project tree, applies ignore patterns from `settings.json`, and builds a `project_snapshot.md` Markdown file. It respects `ai_collaboration.byte_budget` limits and truncates files that exceed the per-file budget.

## Environment pre-flight checker

`src/utils/env_checker.py` (in PR #2) checks for required and optional tools before scaffolding. It returns a boolean and a list of statuses so the CLI can decide whether to block, warn, or proceed.

## Testing strategy

- Unit tests for each utility module (`tests/test_wizard.py`, `tests/test_snapshot.py`, `tests/test_env_checker.py`, etc.).
- CLI integration tests in `tests/test_hatch.py` that call `hatch.main()` with patched `sys.argv`.
- Snapshot generation tests use a temporary directory to avoid touching the repository itself.
- Git operations are mocked in scaffold tests to keep CI fast and side-effect free.

## Extending the system

- Add templates in `hatch.py`.
- Add CLI flags in `hatch.py::main()` and forward them through `run_wizard()` as needed.
- Add configuration knobs in `settings.json` and read them through `Settings.get()`.
- Add corresponding tests and update `README.md` / `CONTRIBUTING.md`.
