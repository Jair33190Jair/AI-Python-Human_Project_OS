#!/usr/bin/env python3
"""R6 pre-pass for /bob-review-script: flag unused imports via ast, stdlib only."""
import ast
import sys


def unused_imports(path: str) -> list[tuple[int, str]]:
    source = open(path, encoding="utf-8").read()
    tree = ast.parse(source, filename=path)

    imported = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split(".")[0]
                imported[name] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    continue
                name = alias.asname or alias.name
                imported[name] = node.lineno

    used = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    used |= {
        node.value.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
    }

    return sorted(
        ((line, name) for name, line in imported.items() if name not in used)
    )


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".py"):
        print("Usage: dead_code_check.py <path/to/script.py>", file=sys.stderr)
        return 2

    findings = unused_imports(sys.argv[1])
    if not findings:
        print("dead_code_check: no unused imports found")
        return 0

    for line, name in findings:
        print(f"{sys.argv[1]}:{line}: unused import '{name}'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
