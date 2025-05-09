import ast

def gen_class_name(table_name: str, class_names: set[str]) -> str:
    class_name = table_name.capitalize()
    
    while class_name in class_names:
        class_name += 'Table'

    return class_name

def optionalize_annotation(annotation: ast.Name | ast.Constant) -> ast.BinOp:
    return ast.BinOp(
        left=annotation,
        op=ast.BitOr(),
        right=ast.Constant(value=None)
    )