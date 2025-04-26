import sqlite3

from sqlmodelgen.ir.ir import (
	ColIR,
	TableIR,
	SchemaIR,
	FKIR
)

def collect_sqlite_ir(sqlite_address: str) -> SchemaIR:
    conn = sqlite3.connect(sqlite_address)
    cursor = conn.cursor()

    table_irs: list[TableIR] = list()

    tablenames = query_table_names(cursor)

    for tablename in tablenames:
        table_info = query_table_info(cursor, tablename)

        table_ir = table_ir_from_info(tablename, table_info)
        table_irs.append(table_ir)

    return SchemaIR(
        table_irs=table_irs
    )

def query_table_names(cursor: sqlite3.Cursor) -> list[str]:
    cursor.execute('SELECT name FROM sqlite_master WHERE type = \'table\'')

    return [elem[0] for elem in cursor.fetchall()]


def query_table_info(cursor: sqlite3.Cursor, tablename: str):
    cursor.execute(f'PRAGMA table_info({tablename})')

    return cursor.fetchall()

def table_ir_from_info(
    tablename: str,
    table_info: list[tuple[int, str, str, int, any, int]]
) -> TableIR:
    col_irs: list[ColIR] = list()

    for col_info in table_info:
        col_name = col_info[1]
        data_type = col_info[2]
        not_null = col_info[3] != 0
        default = col_info[4]
        primary_key = col_info[5] != 0

        col_ir = ColIR(
            name=col_name,
            data_type=data_type,
            primary_key=primary_key,
            not_null=not_null,
            unique=False, # TODO: detect this constraint,
            default=default
        )

        col_irs.append(col_ir)

    return TableIR(
        name=tablename,
        col_irs=col_irs
    )