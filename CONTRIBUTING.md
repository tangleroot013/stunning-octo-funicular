# Contributing to God Mode Scaffolder

Thanks for helping make Waddler OS Pro better. This guide covers how to set up a development environment, run tests, and extend the scaffolder.

## Development setup

The project uses only the Python standard library plus `pytest` for tests.

```bash
git clone https://github.com/tangleroot013/stunning-octo-funicular.git
cd stunning-octo-funicular
python -m venv venv
source venv/bin/activate
python -m pip install pytest
```

## Running tests

```bash
python -m pytest -q
```

All changes should include tests or update existing tests. We use `pytest` fixtures and `monkeypatch` to keep tests isolated and fast.

## Code conventions

- Python 3.7+ compatibility. Use `from __future__ import annotations` when writing modern union types.
- Prefer the standard library. Avoid unnecessary third-party dependencies.
- Place imports at the top of files. Do not import inside functions.
- Keep functions small and focused. Name things descriptively.
- Avoid hard-coding values that already live in `settings.json`.
- Do not commit real API keys, tokens, or credentials. Use placeholders like `ghp_PLACEHOLDER_NEVER_COMMIT_KEYS_DIRECTLY`.

## Project structure

- `hatch.py` — CLI entry point and scaffold engine.
- `src/utils/config_loader.py` — `settings.json` singleton.
- `src/utils/wizard.py` — interactive scaffolding wizard.
- `src/utils/sync_ignores.py` — `.claudeignore` / `.gitignore` synchronization.
- `src/utils/snapshot.py` — `project_snapshot.md` generator.
- `src/utils/env_checker.py` — environment pre-flight checks (in PR #2).
- `settings.json` — central configuration for templates, CI, security, and AI context.
- `tests/` — pytest regression suite.

## Adding a new template

1. Add the template to the `TEMPLATES` dictionary in `hatch.py`.
2. Define `dirs`, `files`, and `extra_deps`.
3. Use `{project_name}`, `{version}`, and `{package_name}` placeholders. These are filled by `render_template`.
4. Add a test to `tests/test_hatch_cli.py` or create a focused test file.

## Adding a new CLI flag

1. Add the argument in `hatch.py::main()`.
2. Wire it into `scaffold()` or `run_wizard()` as appropriate.
3. Add a CLI test in `tests/test_hatch_cli.py`.
4. Update `README.md` and `CONTRIBUTING.md` if the flag changes the developer workflow.

## Adding a settings option

1. Add the key under the appropriate section in `settings.json`.
2. Use `Settings.get("section.sub_key", default)` to read it.
3. Add or update a test that exercises the default and the override path.

## Commit messages

Use conventional commits:

```text
feat: add widget generator
test: cover CLI --widget flag
docs: update README with widget examples
fix: prevent widget over-matching in snapshot exclusion
```

## Security

- Never commit secrets or real tokens.
- Do not disable pre-commit hooks (`--no-verify`) unless explicitly required.
- Secret-detection patterns in generated pre-commit hooks are intentionally noisy; treat any match as a hard stop.

## Pull request process

1. Branch from `main`.
2. Make focused changes with tests.
3. Run `python -m pytest -q` and `python -m py_compile hatch.py src/utils/*.py`.
4. Open a pull request with a clear summary and verification steps.
5. Address review feedback and keep the branch mergeable.
