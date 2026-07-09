import pathlib

# Repository root: src/utils/<file>.py is two levels below the root.
REPO_ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parents[2]
