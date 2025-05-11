import ast


def optionalize_annotation(annotation: ast.Name | ast.Constant) -> ast.BinOp:
    return ast.BinOp(
        left=annotation,
        op=ast.BitOr(),
        right=ast.Constant(value=None)
    )