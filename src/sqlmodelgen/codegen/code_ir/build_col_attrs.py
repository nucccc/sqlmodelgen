import ast
from typing import Callable

from sqlmodelgen.codegen.convert_data_type import convert_data_type
from sqlmodelgen.codegen.code_ir.code_ir import (
    AnnotationType,
    AttributeIR,
    AttrCallIR,
    AttrCallName,
)
from sqlmodelgen.codegen.code_ir.build_common import optionalize_annotation
from sqlmodelgen.ir.ir import ColIR

def attribute_from_col(col_ir: ColIR, column_name_transform: Callable[[str], str] | None = None) -> AttributeIR:
    attr_name = column_name_transform(col_ir.name) if column_name_transform else col_ir.name

    return AttributeIR(
        name=attr_name,
        annotation=build_col_annotation(col_ir),
        call=build_field_call(col_ir, map_name=column_name_transform is not None),
    )


def build_col_annotation(col_ir: ColIR) -> AnnotationType:
    data_type_converted = convert_data_type(col_ir.data_type)

    annotation = ast.Name(data_type_converted)

    if not col_ir.not_null:
        annotation = optionalize_annotation(annotation)

    return annotation


def build_field_call(col_ir: ColIR, map_name=False) -> AttrCallIR | None:
    # TODO: REFACTOR AND FIX THIS
    field_kwords = gen_field_kwords(col_ir, map_name)

    if len(field_kwords) == 0:
        return None

    return AttrCallIR(
        name=AttrCallName.Field,
        kwargs=field_kwords
    )

def gen_field_kwords(col_ir: ColIR, map_name=False) -> list[ast.keyword]:
    '''
    gen_fields_kwords generates a list of keywords which shall go
    into the Field assignment
    '''
    result: list[ast.keyword] = []

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
    if col_ir.data_type == 'uuid':
        result.append(ast.keyword(
            arg='default_factory',
            value=ast.Name('uuid4')
        ))

    if map_name:
        result.append(ast.keyword(
            arg='sa_column_kwargs',
            value=ast.Dict(
                keys=[ast.Constant('name')],
                values=[ast.Constant(col_ir.name)]
            )
        ))
        #result.append(f'sa_column_kwargs={{"name": "{db_name}"}}')

    return result
