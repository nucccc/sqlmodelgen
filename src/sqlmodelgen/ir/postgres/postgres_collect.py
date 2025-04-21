import psycopg
from typing import Iterator

from sqlmodelgen.ir.ir import (
	ColIR,
	TableIR,
	SchemaIR,
	FKIR
)

def collect_postgres_ir(cursor: psycopg.Cursor, schema_name: str = 'public') -> SchemaIR:
    cursor.execute(tables_query(schema_name=schema_name))
    tables_data = cursor.fetchall()

    tables_names = [table_data[1] for table_data in tables_data]

    table_irs: list[TableIR] = list()
    for table_name in tables_names:
        table_irs.append(TableIR(
            name=table_name,
            col_irs=list(collect_columns_ir(
                cursor=cursor,
                table_name=table_name,
                schema_name=schema_name
            ))
        ))

    # TODO: potentially collect contraints regarding foreign keys

    return SchemaIR(
        table_irs=table_irs
    )

def tables_query(schema_name: str) -> str:
    return f'SELECT * FROM pg_catalog.pg_tables WHERE schemaname=\'{schema_name}\''



def collect_columns_ir(
    cursor: psycopg.Cursor,
    table_name: str,
    schema_name: str = 'public'
) -> Iterator[ColIR]:
    cursor.execute(cols_query(table_name, schema_name))

    # NOTE: this code bvasically assumes the cursor not to have a row_factory
    for column_name, column_default, is_nullable, data_type, is_updatable in cursor.fetchall():
        yield ColIR(
            name=column_name, data_type=data_type, primary_key=False, not_null=False
        )

def cols_query(table_name: str, schema_name: str) -> str:
    return f'SELECT column_name, column_default, is_nullable, data_type, is_updatable FROM information_schema.columns WHERE table_schema = \'{schema_name}\' AND table_name = \'{table_name}\''
