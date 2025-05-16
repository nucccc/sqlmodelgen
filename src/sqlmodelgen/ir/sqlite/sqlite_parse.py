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

    # collecting foreign key constraints
    fk_constraints = query_foreign_keys(cursor)

    for tablename in tablenames:
        table_info = query_table_info(cursor, tablename)

        table_ir = table_ir_from_info(tablename, table_info, fk_constraints)
        table_irs.append(table_ir)

    conn.close()

    return SchemaIR(
        table_irs=table_irs
    )

def query_table_names(cursor: sqlite3.Cursor) -> list[str]:
    cursor.execute('SELECT name FROM sqlite_master WHERE type = \'table\'')

    return [elem[0] for elem in cursor.fetchall()]


def query_table_info(cursor: sqlite3.Cursor, tablename: str):
    cursor.execute(f'PRAGMA table_info({tablename})')

    return cursor.fetchall()

def query_foreign_keys(cursor: sqlite3.Cursor) -> dict[str, dict[str, FKIR]]:
    result: dict[str, dict[str, FKIR]] = dict()
    
    cursor.execute('''SELECT
    m.name AS table_name,
    p.name AS parent_table,
    fk.'from' AS column_name,
    fk.'to' AS parent_column_name
FROM
    sqlite_master m
JOIN
    pragma_foreign_key_list(m.name) fk
JOIN
    sqlite_master p ON p.name = fk.'table'
WHERE
    m.type = 'table'
ORDER BY
    m.name,
    fk.id''')

    fk_rows = cursor.fetchall()

    for table_name, target_table, col_name, target_column in fk_rows:
        fk = FKIR(
            target_table=target_table,
            target_column=target_column
        )

        if table_name not in result.keys():
            result[table_name] = dict()

        result[table_name][col_name] = fk

    return result


def table_ir_from_info(
    tablename: str,
    table_info: list[tuple[int, str, str, int, any, int]],
    fk_constraints: dict[str, dict[str, FKIR]]
) -> TableIR:
    col_irs: list[ColIR] = list()

    table_fks = fk_constraints.get(tablename, dict())

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
            default=default,
            foreign_key=table_fks.get(col_name)
        )

        col_irs.append(col_ir)

    return TableIR(
        name=tablename,
        col_irs=col_irs
    )