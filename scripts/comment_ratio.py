#!/usr/bin/env python3
"""Calculate comment-to-code ratio per file and flag comment deserts."""

import ast
from pathlib import Path

def ratio() -> None:
    print("| File | Lines | Comments | Ratio |")
    print("|------|-------|----------|-------|")
    for py in sorted(Path("src").rglob("*.py")):
        text = py.read_text()
        lines = text.splitlines()
        code_lines = len([l for l in lines if l.strip() and not l.strip().startswith("#")])
        comment_lines = len([l for l in lines if l.strip().startswith("#")])
        
        # Count docstrings via AST
        tree = ast.parse(text)
        doc_lines = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node)
                if doc:
                    doc_lines += len(doc.splitlines())
        
        total_comments = comment_lines + doc_lines
        ratio = total_comments / code_lines if code_lines else 0
        
        flag = "🔥" if ratio < 0.05 and code_lines > 20 else ""
        print(f"| {str(py)[:30]:30} | {code_lines:5} | {total_comments:8} | {ratio:5.1%} | {flag}")

if __name__ == "__main__":
    ratio()
