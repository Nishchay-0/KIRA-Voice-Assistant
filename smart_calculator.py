"""Safe basic calculator command support."""

import ast
import operator
import re
from typing import Tuple


_OPERATORS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
              ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod}


def _evaluate(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _evaluate(node.operand)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    raise ValueError("unsupported expression")


def execute_smart_calculation(command: str) -> Tuple[bool, str]:
    match = re.fullmatch(r"\s*(?:calculate|what is|compute)?\s*([0-9+\-*/%.() ]+)\s*\??", command or "", re.IGNORECASE)
    if not match:
        return False, ""
    try:
        result = _evaluate(ast.parse(match.group(1), mode="eval"))
    except (SyntaxError, ValueError, ZeroDivisionError):
        return False, ""
    return True, f"The answer is {result:g}."
