import ast
from typing import Iterable

from sqlmodelgen.codegen.code_ir.code_ir import AttributeIR, AttrCallIR, ModelIR
from sqlmodelgen.codegen.cir_to_full_ast.to_ast_imports import gen_imports


def models_to_ast(models: Iterable[ModelIR]) -> ast.Module:
    cdefs = [model_ir_to_ast(model_ir) for model_ir in models]

    imports = list(gen_imports(cdefs))

    mod = ast.Module(
        body=imports + cdefs,
        type_ignores=[]
    )

    ast.fix_missing_locations(mod)

    return mod


def model_ir_to_ast(model_ir: ModelIR) -> ast.ClassDef:
    body = [
        ast.Assign(
            targets=[ast.Name('__tablename__')],
            value=ast.Constant(model_ir.table_name)
        )
    ]

    # checking if the __table_args__ shall be added
    table_args = gen_table_args(model_ir)
    if table_args is not None:
        body.append(table_args)

    # adding assignment lines
    for attr_ir in model_ir.iter_attrs():
        body.append(
            attr_to_ast(attr_ir)
        )

    return ast.ClassDef(
        name=model_ir.class_name,
        bases=[ast.Name('SQLModel')],
        body=body,
        decorator_list=[],
        keywords=[
            ast.keyword(
                arg='table',
                value=ast.Constant(True)
            )
        ]
    )


def gen_table_args(model_ir: ModelIR) -> ast.Assign | None:
    if len(model_ir.table_args) == 0:
        return None
    
    # at this level we gust generate the unique constraint
    
    return ast.Assign(
        targets=[ast.Name('__table_args__')],
        value=ast.List(
            elts=[table_arg.to_expr() for table_arg in model_ir.table_args]
        )
    )



def attr_to_ast(attr_ir: AttributeIR) -> ast.AnnAssign:
    value = attr_call_to_ast(attr_ir.call) if attr_ir.call is not None else None

    return ast.AnnAssign(
        target=ast.Name(attr_ir.name),
        annotation=attr_ir.annotation,
        value=value,
        simple=1
    )


def attr_call_to_ast(attr_call_ir: AttrCallIR) -> ast.Call:
    return ast.Call(
        func=ast.Name(attr_call_ir.name),
        args=[],
        keywords=attr_call_ir.kwargs
    )
