'''
this module generates sqlmode code from an intermediate representation
'''

import ast
from typing import Callable, Iterable

from sqlmodelgen.ir.ir import SchemaIR
from sqlmodelgen.codegen.code_ir.build_cir import build_model_irs
from sqlmodelgen.codegen.code_ir.code_ir import ModelIR
from sqlmodelgen.codegen.cir_to_full_ast.code_ir_to_ast import models_to_ast


def gen_code(
    schema_ir: Iterable[SchemaIR] | SchemaIR,
    generate_relationships: bool = False,
    table_name_transform: Callable[[str], str] | None = None,
    column_name_transform: Callable[[str], str] | None = None,
) -> str:
    # in case the schema_ir attribute is a single SchemaIR
    if isinstance(schema_ir, SchemaIR):
        model_irs = build_model_irs(schema_ir, generate_relationships, table_name_transform, column_name_transform)
    # otherwise I assume schema_ir is an iterable
    else:
        schema_irs = schema_ir
        model_irs: list[ModelIR] = []
        for schema_ir in schema_irs:
            model_irs += build_model_irs(schema_ir, generate_relationships, table_name_transform, column_name_transform)
    models_ast = models_to_ast(model_irs)

    return ast.unparse(models_ast)
