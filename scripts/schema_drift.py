#!/usr/bin/env python3
"""Detect ORM model drift vs migration files: missing migrations for model changes."""

import ast
import sys
from pathlib import Path

def extract_models(directory: Path) -> set[str]:
    models = set()
    for py in directory.rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if any(isinstance(b, ast.Attribute) and b.attr == "Base" for b in node.bases):
                    models.add(node.name)
    return models

def extract_migrations(directory: Path) -> set[str]:
    migrations = set()
    for py in directory.rglob("*.py"):
        if "migration" in str(py).lower() or "alembic" in str(py).lower():
            text = py.read_text()
            for line in text.splitlines():
                if "create_table" in line or "add_column" in line:
                    # Naive extraction
                    pass
            # Extract table names from migration scripts
            for node in ast.walk(ast.parse(text)):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute) and node.func.attr in ("create_table", "drop_table"):
                        for arg in node.args:
                            if isinstance(arg, ast.Constant):
                                migrations.add(arg.value)
    return migrations

def audit() -> int:
    model_dir = Path("src/models") if Path("src/models").exists() else Path("src")
    migration_dir = Path("migrations") if Path("migrations").exists() else Path("alembic/versions")
    
    if not migration_dir.exists():
        print("ℹ️  No migration directory found.")
        return 0
    
    models = extract_models(model_dir)
    migrations = extract_migrations(migration_dir)
    
    # Check for models without migration coverage
    uncovered = models - migrations
    
    print(f"# Schema Drift Analysis\n")
    print(f"Models:     {len(models)}")
    print(f"Migrations: {len(migrations)}")
    
    if uncovered:
        print(f"\n⚠️  {len(uncovered)} model(s) without migration coverage:")
        for m in uncovered:
            print(f"   - {m}")
        return 1
    
    print("✅ All models have migration coverage.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
