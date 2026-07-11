import os
import ast
import fnmatch
from typing import List

from search import SearchEngine


def web_search(query: str) -> List[dict]:
    se = SearchEngine()
    return se.search(query)


def calculator(expr: str):
    """
    Safely evaluate arithmetic expressions using ast parsing. Supports +,-,*,/,**,(),%,//.
    """
    try:
        node = ast.parse(expr, mode="eval")

        allowed_nodes = (
            ast.Expression,
            ast.BinOp,
            ast.UnaryOp,
            ast.Num,
            ast.Load,
            ast.Add,
            ast.Sub,
            ast.Mult,
            ast.Div,
            ast.Pow,
            ast.Mod,
            ast.FloorDiv,
            ast.USub,
            ast.UAdd,
            ast.Tuple,
            ast.Call,
            ast.Name,
        )

        for n in ast.walk(node):
            # Allow numbers and operators; disallow names except math functions like 'abs' or 'round' if desired
            if isinstance(n, ast.Call):
                raise ValueError("Function calls are not allowed in calculator")
            if isinstance(n, ast.Name):
                raise ValueError("Names are not allowed in calculator")

        compiled = compile(node, "<ast>", "eval")
        return eval(compiled, {"__builtins__": {}})
    except Exception as e:
        return f"Calculator error: {e}"


def file_search(name_pattern: str, path: str = ".", max_results: int = 10):
    """
    Search for files by filename pattern (supports Unix shell-style wildcards) and return paths.
    """
    matches = []
    for root, dirs, files in os.walk(path):
        for filename in files:
            if fnmatch.fnmatch(filename, name_pattern):
                matches.append(os.path.join(root, filename))
                if len(matches) >= max_results:
                    return matches
    return matches
