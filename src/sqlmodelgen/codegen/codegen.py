'''
this module generates sqlmode code from an intermediate representation
'''

import ast

from sqlmodelgen.ir.ir import SchemaIR
from sqlmodelgen.codegen.code_ir.build_cir import build_model_irs
from sqlmodelgen.codegen.cir_to_full_ast.code_ir_to_ast import models_to_ast


def gen_code(schema_ir: SchemaIR, generate_relationships: bool = False) -> str:
    model_irs = build_model_irs(schema_ir, generate_relationships)

    models_ast = models_to_ast(model_irs)

    return ast.unparse(models_ast)