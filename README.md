# God Mode Scaffolder (Waddler OS Pro)

`hatch.py` is a pure-Python project bootstrapper that generates production-ready Python repositories with security hooks, CI pipelines, and token-optimized `.claudeignore` files built in.

## Features

- **Interactive or headless project creation**: run `hatch.py` with no arguments to launch the wizard, or pass a `project_name` to scaffold immediately.
- **Three templates**:
  - `cli` — command-line tools with `argparse` and smoke tests
  - `web` — FastAPI service with `pydantic-settings` and `TestClient` tests
  - `lib` — reusable Python package with `setuptools` build setup
- **Security-first Git hooks**: every scaffold gets a pre-commit hook that scans for secrets, runs `py_compile`, and checks for trailing whitespace.
- **Global Git templates**: `hatch.py --setup-global` installs hooks and a conventional-commit message template for all future repositories.
- **Ignore-file synchronization**: `hatch.py --sync-ignores --dry-run` writes a `.claudeignore` tuned for LLM context windows and a `.gitignore` from `settings.json`.
- **Snapshot generator**: `python src/utils/snapshot.py` builds a `project_snapshot.md` for LLM context, respecting ignore patterns and byte budgets.
- **Settings-driven configuration**: `settings.json` controls templates, ignore patterns, byte budgets, personas, and CI hooks.

## Requirements

- Python 3.7+
- `git`
- `python3-venv` (for the generated virtual environment instructions)

## Installation

```bash
mkdir -p ~/.local/bin
cp hatch.py ~/.local/bin/hatch.py
chmod +x ~/.local/bin/hatch.py
grep -q "alias hatch=" ~/.zshrc || echo "alias hatch='python3 ~/.local/bin/hatch.py'" >> ~/.zshrc
source ~/.zshrc
```

## Usage

### Interactive wizard

```bash
python hatch.py
```

The wizard asks for the project name, template, base directory, coverage threshold, and whether to install the global Git template.

### Direct scaffold

```bash
python hatch.py myproject --template web --path ./projects --coverage-threshold 90
```

### Install global Git hooks and commit message template

```bash
python hatch.py --setup-global
```

### Synchronize ignore files

```bash
python hatch.py --sync-ignores          # writes .claudeignore and .gitignore
python hatch.py --sync-ignores --dry-run  # preview what would change
```

### Generate a context snapshot

```bash
python src/utils/snapshot.py --root .
```

## CLI reference

| Argument / flag | Description |
| --- | --- |
| `project_name` | Optional. Name of the project directory to create. |
| `-p, --path` | Base directory for the new project (default: current directory). |
| `-t, --template` | Template to use: `cli`, `web`, or `lib` (default: `cli`). |
| `--coverage-threshold` | Minimum coverage percentage rendered into the generated CI workflow (default: `85`). |
| `--setup-global` | Install global Git templates and hooks and exit. |
| `--sync-ignores` | Synchronize `.claudeignore` and `.gitignore` from `settings.json`. |
| `--dry-run` | With `--sync-ignores`, show what would change without writing files. |
| `--version` | Print the scaffolder version and exit. |

## Development

Run the test suite:

```bash
python -m pytest -q
```

For the scaffolder itself there is no separate `requirements.txt`; tests only need `pytest`.

## Project layout

```text
hatch.py                    # CLI and scaffold engine
src/
  utils/
    config_loader.py         # settings.json singleton
    snapshot.py              # project_snapshot.md generator
    sync_ignores.py          # .claudeignore / .gitignore sync
    wizard.py                # interactive scaffolding wizard
settings.json               # central configuration
tests/                      # pytest regression suite
```

## Roadmap

- [ ] Environment pre-flight checker ([PR #2](https://github.com/tangleroot013/stunning-octo-funicular/pull/2))
- [ ] GitHub Actions CI workflow for this repository ([PR #3](https://github.com/tangleroot013/stunning-octo-funicular/pull/3))
- [ ] Node.js / npm templates
- [ ] React frontend SPA template
- [ ] Docker Compose environment generators
- [ ] Terraform cloud-platform templates

## License

MIT — by Carter the Duck Developer.
