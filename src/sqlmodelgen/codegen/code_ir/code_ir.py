import ast

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable, Iterator

from sqlmodelgen.codegen.convert_data_type import convert_data_type
from sqlmodelgen.ir.ir import SchemaIR, TableIR, ColIR
from sqlmodelgen.codegen.code_ir.build import (
    gen_class_name,
    optionalize_annotation,
    backpop_keyws
)


AnnotationType = ast.Name | ast.BitOr | ast.Subscript


class AttrCallName(StrEnum):
    Field = 'Field'
    Relationship = 'Relationship'


@dataclass
class AttrCallIR:
    name: AttrCallName
    kwargs: dict[str, any]


@dataclass
class AttributeIR:
    name: str
    annotation: AnnotationType
    call: AttrCallIR | None


@dataclass
class ModelIR:
    class_name: str
    table_name: str
    attrs: list[AttributeIR]
    o2m_rel_attrs: list[AttributeIR]
    m2o_rel_attrs: list[AttributeIR]

    
    def iter_attr_lists(self) -> Iterator[list[AttributeIR]]:
        yield self.attrs
        yield self.o2m_rel_attrs
        yield self.m2o_rel_attrs

    
    def iter_attr_names(self) -> Iterator[str]:
        for attr_list in self.iter_attr_lists():
            for attr in attr_list:
                yield attr.name


    def is_attr_name_used(self, candidate_name: str) -> bool:
        # TODO: this maybe at a point for performance reasons there could be a
        # set or some other data strcture to help the performances and avoid
        # linearly iterating over attribute names
        for attr_name in self.iter_attr_names():
            if attr_name == candidate_name:
                return True
        return False


def build_model_irs(schema_ir: SchemaIR, gen_relationships: bool) -> list[ModelIR]:
    class_names: set[str] = set()
    models_by_table_name: dict[str, ModelIR] = dict()

    for table_ir in schema_ir.table_irs:
        model_ir = build_model_ir(table_ir=table_ir, class_names=class_names)

        models_by_table_name[model_ir.table_name] = model_ir
        
        class_names.add(model_ir.class_name)

    if gen_relationships:
        # TODO: implement
        add_relationships_attrs(schema_ir, models_by_table_name)

    return list(models_by_table_name.values())


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

    
def build_model_ir(table_ir: TableIR, class_names: set[str]) -> ModelIR:
    return ModelIR(
        class_name=gen_class_name(table_ir.name, class_names),
        table_name=table_ir.name,
        attrs=[attribute_from_col(col_ir) for col_ir in table_ir.col_irs]
    )


def attribute_from_col(col_ir: ColIR) -> AttributeIR:
    return AttributeIR(
        name=col_ir.name,
        annotation=build_col_annotation(col_ir),
        call=build_field_call(col_ir)
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


def build_col_annotation(col_ir: ColIR) -> AnnotationType:
    data_type_converted = convert_data_type(col_ir.data_type)

    annotation = ast.Name(data_type_converted)

    if not col_ir.not_null:
        annotation = optionalize_annotation(annotation)

    return annotation


def build_field_call(col_ir: ColIR) -> AttrCallIR | None:
    field_kwords = gen_field_kwords(col_ir)

    if len(field_kwords) == 0:
        return None
    
    return ast.Call(
        func=ast.Name('Field'),
        args=[],
        keywords=field_kwords
    )

def gen_field_kwords(col_ir: ColIR) -> list[ast.keyword]:
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
    if col_ir.data_type == 'uuid':
        result.append(ast.keyword(
            arg='default_factory',
            value=ast.Name('uuid4')
        ))

    return result