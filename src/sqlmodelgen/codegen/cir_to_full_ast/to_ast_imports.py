'''
when generating an import this shall somehow handle all the generation
of import ast nodes from the generated class definitions
'''

import ast
from itertools import chain
from typing import Iterable, Iterator

AST_IMPORT_TYPE = ast.Import | ast.ImportFrom

TYPE_IMPORTS = {
    'datetime': ast.ImportFrom(
        module='datetime',
        names=[
            ast.alias('datetime')
        ]
    ),
    'UUID': ast.ImportFrom(
        module='uuid',
        names=[
            ast.alias('UUID'),
            ast.alias('uuid4')
        ]
    )
}

def gen_imports(cdefs: Iterable[ast.ClassDef]) -> Iterator[AST_IMPORT_TYPE]:
    data_types_names = set(chain(*map(_iter_data_type_names, cdefs)))

    call_names = set(chain(*map(_iter_call_names, cdefs)))

    yield gen_sqlmodel_import(call_names)

    for data_type_name in data_types_names:
        data_type_import = TYPE_IMPORTS.get(data_type_name)
        if data_type_import is not None:
            yield data_type_import


def gen_sqlmodel_import(call_names: set[str]) -> ast.ImportFrom:
    sqlmodel_import = ast.ImportFrom(
        module='sqlmodel',
        names=[
            ast.alias('SQLModel')
        ]
    )

    if 'Field' in call_names:
        sqlmodel_import.names.append(
            ast.alias('Field')
        )

    if 'Relationship' in call_names:
        sqlmodel_import.names.append(
            ast.alias('Relationship')
        )

    if 'UniqueConstraint' in call_names:
        sqlmodel_import.names.append(
            ast.alias('UniqueConstraint')
        )

    return sqlmodel_import


def _iter_data_type_names(cdef: ast.ClassDef) -> Iterator[str]:
    for ann_as in filter(lambda x: isinstance(x, ast.AnnAssign), cdef.body):
        ann = ann_as.annotation
        yield from (
            name.id
            for name in filter(lambda x: isinstance(x, ast.Name), ast.walk(ann))
        )

def _iter_call_names(cdef: ast.ClassDef) -> Iterator[str]:
    # considering the annotated assignments
    for ann_as in filter(lambda x: isinstance(x, ast.AnnAssign), cdef.body):
        value = ann_as.value
        if isinstance(value, ast.Call):
            if isinstance(value.func, ast.Name):
                yield value.func.id

    # consindering the table args
    for assign in filter(lambda x: isinstance(x, ast.Assign), cdef.body):
        for call in filter(lambda x: isinstance(x, ast.Call), ast.walk(assign.value)):
            if isinstance(call.func, ast.Name):
                yield call.func.id
