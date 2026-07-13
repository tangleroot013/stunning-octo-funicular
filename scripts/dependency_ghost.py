#!/usr/bin/env python3
"""Find imports in src/ with no matching package in requirements.txt."""

import ast
import sys
from pathlib import Path

def scan() -> int:
    imports = set()
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            if isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
    
    req = Path("requirements.txt")
    if not req.exists():
        print("ℹ️  No requirements.txt found.")
        return 0
    listed = set()
    for line in req.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            listed.add(line.split("==")[0].split("[")[0].strip().replace("-", "_"))
    
    stdlib = {"os", "sys", "json", "re", "pathlib", "typing", "collections", "subprocess", "datetime", "math", "tempfile", "threading", "urllib", "string", "hashlib", "importlib", "ast", "inspect", "warnings", "itertools", "functools", "enum", "dataclasses", "contextlib", "copy", "pickle", "io", "base64", "binascii", "csv", "xml", "html", "http", "email", "uuid", "secrets", "random", "statistics", "decimal", "fractions", "numbers", "abc", "types", "weakref", "gc", "atexit", "signal", "time", "calendar", "locale", "codecs", "encodings", "keyword", "token", "tokenize", "tabnanny", "pyclbr", "py_compile", "compileall", "dis", "pickletools", "bdb", "pdb", "profile", "cProfile", "pstats", "trace", "tracemalloc", "doctest", "unittest", "test", "lib2to3", "difflib", "filecmp", "linecache", "macpath", "shutil", "macpath", "fnmatch", "glob", "pathlib", "stat", "fileinput", "mmap", "code", "codeop", "zipfile", "tarfile", "gzip", "bz2", "lzma", "zipimport", "pkgutil", "modulefinder", "runpy", "importlib", "importlib_metadata", "importlib_resources"}
    
    ghosts = imports - listed - stdlib
    if ghosts:
        print(f"⚠️  {len(ghosts)} import(s) not in requirements.txt:")
        for g in sorted(ghosts):
            print(f"   {g}")
        return 1
    print("✅ All imports accounted for.")
    return 0

if __name__ == "__main__":
    sys.exit(scan())
