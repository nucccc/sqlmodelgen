import ast

from typing import Iterator, Iterable

from sqlmodelgen.codegen.code_ir.code_ir import (
    AttributeIR,
    AttrCallIR,
    AttrCallName,
    ModelIR
)
from sqlmodelgen.codegen.code_ir.build_common import optionalize_annotation
from sqlmodelgen.ir.ir import SchemaIR


def add_relationships_attrs(
    schema_ir: SchemaIR,
    models_by_table_name: dict[str, ModelIR]
):
    for table_ir in schema_ir.table_irs:
        for col_ir in table_ir.col_irs:
            if col_ir.foreign_key is None:
                continue

            o2m_model = models_by_table_name.get(table_ir.name)
            m2o_model = models_by_table_name.get(col_ir.foreign_key.target_table)

            # NOTE: I don't like this thing, let's say that one day there is independence
            # between col_ir names and the attributes, maybe I should think again
            # about this
            if o2m_model is None or m2o_model is None:
                continue

            add_relationship_attrs(
                o2m_model=o2m_model,
                m2o_model=m2o_model,
                o2m_var_name=col_ir.name
            )


def add_relationship_attrs(
    o2m_model: ModelIR,
    m2o_model: ModelIR,
    o2m_var_name: str
):
    o2m_name = determine_o2m_name(o2m_var_name, o2m_model)
    m2o_name = determine_m2o_name(o2m_model.table_name, m2o_model)

    o2m_model.o2m_rel_attrs.append(
        o2m_rel_attribute(o2m_name, m2o_model.class_name, m2o_name)
    )
    
    m2o_model.m2o_rel_attrs.append(
        m2o_rel_attribute(m2o_name, o2m_model.class_name, o2m_name)
    )


def gen_o2m_candidate_names(o2m_var_name: str) -> Iterator[str]:
    var_name = o2m_var_name
    
    if var_name.endswith('_id'):
        var_name = var_name[:-3]
        yield var_name
    elif var_name.endswith('id'):
        var_name = var_name[:-2]
        yield var_name

    var_name += '_rel'
    yield var_name

    counter = 0
    while True:
        yield f'{var_name}{counter}'
        counter += 1


def gen_m2o_candidate_names(vassal_table_name: str) -> Iterator[str]:
    var_name = vassal_table_name + 's'
    yield var_name

    counter = 0
    while True:
        yield f'{var_name}{counter}'
        counter += 1


def first_valid_rel_name(
    name_gen: Iterable[str],
    model: ModelIR
) -> str:
    for name in name_gen:
        if not model.is_attr_name_used(name):
            return name


def determine_o2m_name(o2m_var_name: str, o2m_model: ModelIR) -> str:
    '''
    determine_o2m_name attempts to generate a meaningful name for an o2m
    relationship while ensuring it does not still exist inside the current model
    '''
    return first_valid_rel_name(
        gen_o2m_candidate_names(o2m_var_name),
        model=o2m_model
    )


def determine_m2o_name(vassal_table_name: str, m2o_model: ModelIR) -> str:
    return first_valid_rel_name(
        gen_m2o_candidate_names(vassal_table_name),
        model=m2o_model
    )


def o2m_rel_attribute(
    name: str,
    target_class_name: str,
    m2o_attr_name: str
) -> AttributeIR:
    return AttributeIR(
        name=name,
        annotation=optionalize_annotation(ast.Constant(target_class_name)),
        call=AttrCallIR(
            AttrCallName.Relationship,
            kwargs=backpop_keyws(m2o_attr_name)
        )
    )


def m2o_rel_attribute(
    name: str,
    vassal_class_name: str,
    o2m_attr_name: str
) -> AttributeIR:
    return AttributeIR(
        name=name,
        annotation=ast.Subscript(
            value=ast.Name('list'),
            slice=ast.Constant(value=vassal_class_name)
        ),
        call=AttrCallIR(
            AttrCallName.Relationship,
            kwargs=backpop_keyws(o2m_attr_name)
        )
    )


def backpop_keyws(backpop: str) -> list[ast.keyword]:
    return [
        ast.keyword(
            arg='back_populates',
            value=ast.Constant(value=backpop)
        )
    ]