from collections.abc import Iterator

from sqlmodelgen.codegen.code_ir.code_ir import UniqueTableArgIR, SchemaNameArgIR
from sqlmodelgen.ir.ir import TableIR

def build_table_args(table_ir: TableIR, schema_name: str | None) -> Iterator[UniqueTableArgIR]:
    yield from build_unique_constraints(table_ir)
    
    # yield the schema name at last in order to be consistent
    # with the sqlalchemy requirement of having the schema
    # dictionary at last
    if schema_name is not None and schema_name != 'public':
        yield SchemaNameArgIR(schema_name=schema_name)
    


def build_unique_constraints(table_ir: TableIR) -> Iterator[UniqueTableArgIR]:
    # TODO: still no code tp generate unique for multiple columns
    
    yield from (
        UniqueTableArgIR([col_ir.name])
        for col_ir in table_ir.col_irs
        if col_ir.unique and not col_ir.primary_key
    )