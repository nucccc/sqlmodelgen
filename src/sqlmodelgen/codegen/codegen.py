'''
this module generates sqlmode code from an intermediate representation
'''

import ast
from dataclasses import dataclass
from itertools import chain
from typing import Iterable, Iterator

from sqlmodelgen.ir.ir import SchemaIR, ColIR
from sqlmodelgen.codegen.classes import Model, arrange_relationships
from sqlmodelgen.codegen.convert_data_type import convert_data_type
from sqlmodelgen.codegen.to_ast import gen_ast


DEFAULT_TAB_LEVEL = '\t'

'''def _iter_data_types(models: list[Model]) -> Iterator[str]:
    for model in models:
        pass
        #for model.'''


@dataclass
class ImportsNecessary:
    field: bool = False
    relationship: bool = False

    def iter_to_import(self) -> Iterator[str]:
        if self.field:
            yield 'Field'
        if self.relationship:
            yield 'Relationship'

    def absorb_data_types(models: list[Model]):
        pass


def gen_code(schema_ir: SchemaIR, generate_relationships: bool = False) -> str:
    model_irs = build_model_irs(schema_ir.table_irs)

    # TODO: verify that this if is correct
    if generate_relationships:
        arrange_relationships(model_irs)

        for model_ir in model_irs:
            for rel in chain(model_ir.m2o_relationships, model_ir.o2m_relationships):
                rel.determine_rel_names()

    models_ast = gen_ast(model_irs)

    return ast.unparse(models_ast)


def build_model_irs(table_irs: Iterable[Model]) -> list[Model]:
    model_irs: list[Model] = list()
    class_names: set[str] = set()

    for table_ir in table_irs:
        model_ir = Model(table_ir, class_names)
        class_names.add(model_ir.class_name)
        model_irs.append(model_ir)

    return model_irs
