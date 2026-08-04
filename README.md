# God Mode Scaffolder

A resilient Python scaffolding engine for secure, reproducible project bootstraps.

This repository provides a lightweight command-line scaffolder with:

- `hatch` CLI for rapid project creation
- secure Git pre-commit hooks for secret and syntax protection
- automated `.claudeignore` / `.gitignore` sync from a single configuration source
- opinionated CI workflow generation with Ruff / Black / Pytest support
- interactive and non-interactive modes for autonomous or guided setup

## Quick start

```bash
cd stunning-octo-funicular
python3 -m pip install -e .
```

Then run the scaffold command:

```bash
hatch --help
```

Create a new CLI project interactively:

```bash
hatch
```

Create a new library project with a specific name:

```bash
hatch mylib -t lib
```

Synchronize ignore files from repository configuration:

```bash
hatch --sync-ignores --path .
```

Install global Git hooks and commit templates:

```bash
hatch --setup-global
```

## Features

- **Safe defaults**: project scaffolds include Git ignore hygiene, CI workflow templates, and quality automation out of the box.
- **Self-healing ignore sync**: `.claudeignore` and `.gitignore` are derived from centralized settings and kept in sync.
- **Interactive wizard**: run without arguments for step-by-step setup.
- **CLI-first design**: install as a Python package and run `hatch` directly.

## Developer workflow

Run the tests with:

```bash
python3 -m pytest -c /dev/null tests -q
```

Because this repository uses a condensed pytest configuration, the `-c /dev/null` flag is a reliable local invocation when `pytest-cov` is not installed.

## Packaging

This repo uses a standard Python packaging layout. After installation, the CLI entry point is exposed as:

```bash
hatch
```

You can also invoke directly without installation:

```bash
python3 -m src.hatch --help
```

## Project structure

- `src/hatch.py` — core CLI engine and scaffolding orchestration
- `src/utils/` — support modules for settings, ignore syncing, AI-safe context generation, and interactive prompts
- `tests/` — regression and behavior coverage for safe scaffolding

## License

MIT
