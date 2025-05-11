'''
wouldn't it be nice if the models were to just be
transformed into asts?

let's try
'''

import ast
from typing import Iterable, Iterator

from sqlmodelgen.ir.ir import ColIR
from sqlmodelgen.codegen.classes import Model
from sqlmodelgen.codegen.convert_data_type import convert_data_type
#from sqlmodelgen.codegen.to_ast_imports import gen_imports


def gen_ast(models: Iterable[Model]) -> ast.Module:
    cdefs = list(map(model_to_ast, models))

    imports = list(gen_imports(cdefs))

    mod = ast.Module(
        body=imports + cdefs,
        type_ignores=[]
    )

    ast.fix_missing_locations(mod)

    return mod


def model_to_ast(model: Model) -> ast.ClassDef:
    body = [
        ast.Assign(
            targets=[ast.Name('__tablename__')],
            value=ast.Constant(model.table_name)
        )
    ]

    # adding assignment lines
    for col_ir in model.ir.col_irs:
        body.append(
            gen_col_expr(col_ir)
        )

    # then adding relationship lines
    for rel_expr in gen_rel_exprs(model):
        body.append(rel_expr)    

    return ast.ClassDef(
        name=model.class_name,
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


def gen_col_expr(col_ir: ColIR) -> ast.AnnAssign:
    data_type_converted = convert_data_type(col_ir.data_type)

    annotation = ast.Name(data_type_converted)

    if not col_ir.not_null:
        # TODO: invoke optionalize annotation
        annotation = ast.BinOp(
            left=annotation,
            op=ast.BitOr(),
            right=ast.Constant(value=None)
        )

    return ast.AnnAssign(
        target=ast.Name(col_ir.name),
        annotation=annotation,
        value=gen_col_field(col_ir, data_type_converted),
        simple=1
    )


def gen_col_field(col_ir: ColIR, data_type_converted: str) -> ast.Call | None:
    kwords = gen_field_kwords(col_ir, data_type_converted)

    if len(kwords) == 0:
        return None

    return ast.Call(
        func=ast.Name('Field'),
        args=[],
        keywords=kwords
    )


def gen_field_kwords(col_ir: ColIR, data_type_converted: str) -> list[ast.keyword]:
    '''
    gen_fields_kwords generates a list of keywords which shall go
    into the Field assignment
    '''
    result: list[str] = list()

    if col_ir.primary_key:
        result.append(ast.keyword(
            arg='primary_key',
            value=ast.Constant(value=True)
        ))
        #result.append('primary_key=True')

    if col_ir.foreign_key is not None:
        result.append(ast.keyword(
            arg='foreign_key',
            value=ast.Constant(
                value=f'{col_ir.foreign_key.target_table}.{col_ir.foreign_key.target_column}'
            )
        ))
        #result.append(f'foreign_key="{col_ir.foreign_key.target_table}.{col_ir.foreign_key.target_column}"')

    # TODO: do I need the default factory when this is a foreign key?

    # the specific case in which a default factory of uuid is needed
    if data_type_converted == 'UUID':
        result.append(ast.keyword(
            arg='default_factory',
            value=ast.Name('uuid4')
        ))

    return result


def gen_rel_exprs(model: Model) -> Iterator[ast.AnnAssign]:
    for rel in model.m2o_relationships:
        line = gen_rel_m2o(
            m2o_rel_name=rel.m2o_rel_name,
            o2m_class_name=rel.o2m_model.class_name,
            o2m_rel_name=rel.o2m_rel_name
        )

        yield line

    for rel in model.o2m_relationships:
        line = gen_rel_o2m(
            o2m_rel_name=rel.o2m_rel_name,
            m2o_class_name=rel.m2o_model.class_name,
            m2o_rel_name=rel.m2o_rel_name
        )
        
        yield line

    
def gen_rel_m2o(
    m2o_rel_name: str,
    o2m_class_name: str,
    o2m_rel_name: str
) -> ast.AnnAssign:
    return ast.AnnAssign(
        target=ast.Name(m2o_rel_name),
        annotation=ast.Subscript(
            value=ast.Name('list'),
            slice=ast.Constant(value=o2m_class_name)
        ),
        value=ast.Call(
            func=ast.Name('Relationship'),
            args=[],
            keywords=backpop_keyws(o2m_rel_name)
        ),
        simple=1
    )
    # return f'{tab_level}{m2o_rel_name}: list[\'{o2m_class_name}\'] = Relationship(back_populates=\'{o2m_rel_name}\')'


def gen_rel_o2m(
    o2m_rel_name: str,
    m2o_class_name: str,
    m2o_rel_name: str
) -> str:
    return ast.AnnAssign(
        target=ast.Name(o2m_rel_name),
        annotation=optionalize_annotation(ast.Constant(value=m2o_class_name)),
        value=ast.Call(
            func=ast.Name('Relationship'),
            args=[],
            keywords=backpop_keyws(m2o_rel_name)
        ),
        simple=1
    )
    # return f'{tab_level}{o2m_rel_name}: \'{m2o_class_name}\' | None = Relationship(back_populates=\'{m2o_rel_name}\')'


def backpop_keyws(backpop: str) -> list[ast.keyword]:
    return [
        ast.keyword(
            arg='back_populates',
            value=ast.Constant(value=backpop)
        )
    ]


def optionalize_annotation(annotation: ast.Name | ast.Constant) -> ast.BinOp:
    return ast.BinOp(
        left=annotation,
        op=ast.BitOr(),
        right=ast.Constant(value=None)
    )
