#!/usr/bin/env python3
"""Granular type annotation coverage: params, returns, variables, and generics."""

import ast
from pathlib import Path

def audit() -> None:
    total_funcs = typed_params = typed_returns = typed_vars = 0
    
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                total_funcs += 1
                if node.returns:
                    typed_returns += 1
                typed_params += sum(1 for a in node.args.args if a.annotation)
            
            if isinstance(node, ast.AnnAssign):
                typed_vars += 1
    
    print("# Type Coverage\n")
    print(f"Functions:     {total_funcs}")
    print(f"Typed params:  {typed_params} ({typed_params/max(total_funcs,1)*100:.0f}%)")
    print(f"Typed returns: {typed_returns} ({typed_returns/max(total_funcs,1)*100:.0f}%)")
    print(f"Typed vars:    {typed_vars}")
    overall = (typed_params + typed_returns) / max(total_funcs * 2, 1) * 100
    print(f"\nOverall: {overall:.0f}%")

if __name__ == "__main__":
    audit()
