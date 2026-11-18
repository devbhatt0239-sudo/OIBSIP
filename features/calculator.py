"""Safe arithmetic evaluator; never uses eval()."""
import ast
import operator

_ALLOWED = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Mod: operator.mod, ast.Pow: operator.pow,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def calculate(expression: str):
    text = expression.lower()
    replacements = {
        "multiplied by": "*", "multiply by": "*", "times": "*",
        "divided by": "/", "divide by": "/", "plus": "+",
        "minus": "-", "modulus": "%", "power": "**",
    }
    for word, symbol in replacements.items():
        text = text.replace(word, symbol)

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED:
            return _ALLOWED[type(node.op)](visit(node.left), visit(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED:
            return _ALLOWED[type(node.op)](visit(node.operand))
        raise ValueError("Only basic arithmetic expressions are supported.")

    tree = ast.parse(text, mode="eval")
    return visit(tree)
