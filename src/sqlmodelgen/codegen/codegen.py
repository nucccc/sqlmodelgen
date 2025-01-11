'''
this module generates sqlmode code from an intermediate representation
'''

from dataclasses import dataclass
from typing import Iterable, Iterator

from sqlmodelgen.ir.ir import SchemaIR, TableIR, ColIR
from sqlmodelgen.codegen.classes import Model, Relationship, arrange_relationships


DEFAULT_TAB_LEVEL = '\t'


@dataclass
class ImportsNecessary:
    field: bool = False
    relationship: bool = False

    def iter_to_import(self) -> Iterator[str]:
        if self.field:
            yield 'Field'
        if self.relationship:
            yield 'Relationship'


def gen_code(schema_ir: SchemaIR) -> str:
    code_generator = CodeGen(schema_ir)
    return code_generator.generate_code()



def generate_sqlmodels(schema_ir: SchemaIR, generate_relationships: bool = False) -> str:
    # TODO: probably this declaration is unuseful
    imports_necessary = ImportsNecessary()

    model_irs = build_model_irs(schema_ir.table_irs)

    arrange_relationships(model_irs)

    return _gen_code(model_irs, generate_relationships)


def _gen_code(models: list[Model], generate_relationships: bool) -> str:
    imports_necessary = ImportsNecessary()

    models_code = _gen_models_code(models, generate_relationships, imports_necessary)
    import_code = _gen_import_code(imports_necessary)

    return f'{import_code}\n\n{models_code}'


def _gen_models_code(
    models: list[Model],
    generate_relationships: bool,
    imports_necessary: ImportsNecessary
) -> str:
    models_codes: list[str] = list()

    for model in models:
        model_code = _gen_model_code(model, generate_relationships, imports_necessary)
        models_codes.append(model_code)

    return '\n\n'.join(models_codes)

def _gen_model_code(
    model: Model,
    generate_relationships: bool,
    imports_necessary: ImportsNecessary
) -> str:
    header_code = f'''class {model.class_name}(SQLModel, table = True):
\t__tablename__ = '{model.table_name}' '''
    
    model_lines = _gen_model_lines(model, generate_relationships, imports_necessary)

    cols_code = '\n'.join(model_lines)
    code = f'{header_code}\n{cols_code}'

    return code


def _gen_model_lines(
    model: Model,
    generate_relationships: bool,
    imports_necessary: ImportsNecessary
) -> list[str]:
    cols_lines = _gen_cols_lines(model, imports_necessary)
    rels_lines = _gen_rels_lines(model, imports_necessary) if generate_relationships else []

    return cols_lines + rels_lines

def _gen_cols_lines(
    model: Model,
    imports_necessary: ImportsNecessary
) -> list[str]:
    cols_lines: list[str] = list()
    for col_ir in model.ir.col_irs:
        col_line, used_field_in_col = gen_col_line(col_ir)
        cols_lines.append(col_line)
        if used_field_in_col:
            imports_necessary.field = True
    
    return cols_lines

def _gen_rels_lines(
    model: Model,
    imports_necessary: ImportsNecessary
) -> list[str]:
    rels_lines: list[str] = list()

    # TODO: verify this!!!
    for rel in model.relationships:
        rel.determine_rel_names()

        rel_name = rel.rel_name
        class_name = rel.main_table.name
        foreign_rel_name = rel.foreign_rel_name
        line = gen_rel_line_list(rel_name, class_name, foreign_rel_name)

        rels_lines.append(line)

        imports_necessary.relationship = True

    for foreign_rel in model.referencing_relationships:
        foreign_rel.determine_rel_names()

        rel_name = foreign_rel.rel_name
        foreign_rel_name = foreign_rel.foreign_rel_name
        foreign_class_name = foreign_rel.foreign_table.name
        
        line = gen_rel_line_one(foreign_rel_name, foreign_class_name, rel_name)
        
        rels_lines.append(line)

        imports_necessary.relationship = True
    
    return rels_lines

def _gen_import_code(imports_necessary) -> str:
    import_code = 'from sqlmodel import SQLModel'

    additional_imports = ', '.join(imports_necessary.iter_to_import())
    if additional_imports:
        import_code = import_code + ', ' + additional_imports

    return import_code

def build_model_irs(table_irs: Iterable[Model]) -> list[Model]:
    model_irs: list[Model] = list()
    class_names: set[str] = set()

    for table_ir in table_irs:
        model_ir = Model(table_ir, class_names)
        class_names.add(model_ir.class_name)
        model_irs.append(model_ir)

    return model_irs


def gen_rels_lines(table_ir: TableIR) -> list[str]:
    rels_lines: list[str] = list()

    for rel in table_ir.relationships:
        rel.determine_rel_names()
        rel_name = rel.rel_name
        class_name = rel.main_table.name
        foreign_rel_name = rel.foreign_rel_name
        rels_lines.append(f'{rel_name}: list[\'{class_name}\'] = Relationship(back_populates=\'{foreign_rel_name}\')')
    for foreign_rel in table_ir.foreign_relationships:
        foreign_rel.determine_rel_names()
        rel_name = foreign_rel.rel_name
        foreign_rel_name = foreign_rel.foreign_rel_name
        foreign_class_name = foreign_rel.foreign_table.name
        rels_lines.append(f'{foreign_rel_name}: \'{foreign_class_name}\' | None = Relationship(back_populates=\'{rel_name}\')')


def gen_rel_line_list(
    rel_name: str,
    class_name: str,
    foreign_rel_name: str,
    tab_level: str = DEFAULT_TAB_LEVEL
) -> str:
    return f'{tab_level}{rel_name}: list[\'{class_name}\'] = Relationship(back_populates=\'{foreign_rel_name}\')'


def gen_rel_line_one(
    foreign_rel_name: str,
    foreign_class_name: str,
    rel_name: str,
    tab_level: str = DEFAULT_TAB_LEVEL
) -> str:
    return f'{tab_level}{foreign_rel_name}: \'{foreign_class_name}\' | None = Relationship(back_populates=\'{rel_name}\')'


def gen_col_line(col_ir: ColIR) -> tuple[str, bool]:
    used_field = False
    
    col_line = f'\t{col_ir.name}: {col_ir.data_type}'
    if not col_ir.not_null:
        col_line += ' | None'

    # generating field keywords
    fields_kwords_list: list[str] = gen_fields_kwords(col_ir)

    # in case i have any field keyword then I need to add a Field
    # assignemnt, in such case I flag the usage of the field keyword
    if len(fields_kwords_list) > 0:
        fields_kwords = ', '.join(fields_kwords_list)
        col_line += f' = Field({fields_kwords})'
        used_field = True

    return col_line, used_field

def gen_fields_kwords(col_ir: ColIR) -> list[str]:
    '''
    gen_fields_kwords generates a list of keywords which shall go
    into the Field assignment
    '''
    result: list[str] = list()

    if col_ir.primary_key:
        result.append('primary_key=True')

    if col_ir.foreign_key is not None:
        result.append(f'foreign_key="{col_ir.foreign_key.target_table}.{col_ir.foreign_key.target_column}"')

    return result