# such try catch statements serves the puspose of allowing typing with postgres
# to be spred across the module

import psycopg

from dataclasses import dataclass
from typing import Iterator

from sqlmodelgen.ir.ir import (
	ColIR,
	TableIR,
	SchemaIR,
	FKIR
)

@dataclass
class ContraintsData:
    uniques: dict[str, set[str]]
    primary_keys: dict[str, set[str]]
    foreingn_keys: dict[str, dict[str, FKIR]]

    def is_unique(self, table_name: str, column_name: str) -> bool:
        return column_name in self.uniques.get(table_name, set())
    
    def is_primary_key(self, table_name: str, column_name: str) -> bool:
        return column_name in self.primary_keys.get(table_name, set())
    
    def get_foreign_key(self, table_name: str, column_name: str) -> FKIR | None:
        table_fks = self.foreingn_keys.get(table_name)

        if table_fks is None:
            return None
        
        return table_fks.get(column_name)


def collect_postgres_ir(postgres_conn_addr: str, schema_name: str = 'public') -> SchemaIR:    

    conn = psycopg.connect(postgres_conn_addr)
    cursor = conn.cursor()

    constraints = collect_contraints(cursor, schema_name)
    
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
                schema_name=schema_name,
                constraints=constraints
            ))
        ))

    # TODO: potentially collect contraints regarding foreign keys

    conn.close()

    return SchemaIR(
        table_irs=table_irs
    )

def tables_query(schema_name: str) -> str:
    return f'SELECT * FROM pg_catalog.pg_tables WHERE schemaname=\'{schema_name}\''



def collect_columns_ir(
    cursor: psycopg.Cursor,
    table_name: str,
    schema_name: str,
    constraints: ContraintsData
) -> Iterator[ColIR]:
    cursor.execute(cols_query(table_name, schema_name))

    # NOTE: this code bvasically assumes the cursor not to have a row_factory
    for column_name, column_default, is_nullable, data_type, is_updatable in cursor.fetchall():
        yield ColIR(
            name=column_name,
            data_type=data_type,
            primary_key=constraints.is_primary_key(table_name, column_name),
            not_null=(is_nullable == 'NO'),
            unique=constraints.is_unique(table_name, column_name),
            foreign_key=constraints.get_foreign_key(table_name, column_name)
        )


def cols_query(table_name: str, schema_name: str) -> str:
    return f'SELECT column_name, column_default, is_nullable, data_type, is_updatable FROM information_schema.columns WHERE table_schema = \'{schema_name}\' AND table_name = \'{table_name}\''


def collect_contraints(cursor: psycopg.Cursor, schema_name: str) -> ContraintsData:
    # TODO: possibly all of that stuff could be made async at a point
    return ContraintsData(
        uniques=collect_uniques(cursor, schema_name),
        primary_keys=collect_primary_keys(cursor, schema_name),
        foreingn_keys=collect_foreign_keys(cursor, schema_name)
    )


def collect_uniques(cursor: psycopg.Cursor, schema_name: str) -> dict[str, set[str]]:
    cursor.execute(f'''SELECT
    tc.table_name, 
    tc.constraint_name,
    kcu.column_name
FROM 
    information_schema.table_constraints tc
JOIN 
    information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
WHERE 
    tc.constraint_type = 'UNIQUE' AND tc.table_schema = '{schema_name}'
ORDER BY 
    tc.table_schema, 
    tc.table_name''')

    rows = cursor.fetchall()

    result: dict[str, set[str]] = dict()

    for table_name, _, column_name in rows:
        if table_name not in result.keys():
            result[table_name] = set()
        result[table_name].add(column_name)

    return result


def collect_primary_keys(cursor: psycopg.Cursor, schema_name: str) -> dict[str, set[str]]:
    cursor.execute(f'''SELECT
    tc.table_name, 
    tc.constraint_name,
    kcu.column_name
FROM 
    information_schema.table_constraints tc
JOIN 
    information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
WHERE 
    tc.constraint_type = 'PRIMARY KEY' AND tc.table_schema = '{schema_name}'
ORDER BY 
    tc.table_schema, 
    tc.table_name''')

    rows = cursor.fetchall()

    result: dict[str, set[str]] = dict()

    for table_name, _, column_name in rows:
        if table_name not in result.keys():
            result[table_name] = set()
        result[table_name].add(column_name)

    return result


def collect_foreign_keys(
    cursor: psycopg.Cursor,
    schema_name: str
) -> dict[str, dict[str, FKIR]]:
    # TODO: extend this to external tables from other schemas (it appears
    # in postgres one can have foreign key constraints between tables of
    # different schemas)
    cursor.execute(f'''SELECT
    tc.table_schema,
    tc.table_name,
    tc.constraint_name,
    kcu.column_name,
    ccu.table_schema AS foreign_table_schema,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM
    information_schema.table_constraints tc
JOIN
    information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN
    information_schema.constraint_column_usage ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE
    tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = '{schema_name}'
ORDER BY
    tc.table_name''')

    rows = cursor.fetchall()

    result: dict[str, dict[str, FKIR]] = dict()

    for (
        table_schema,
        table_name,
        constraint_name,
        column_name,
        foreign_table_schema,
        foreign_table_name,
        foreign_column_name
    ) in rows:
        table_fks = result.get(table_name)
        if table_fks is None:
            table_fks = dict()
            result[table_name] = table_fks

        table_fks[column_name] = FKIR(
            target_table=foreign_table_name,
            target_column=foreign_column_name
        )

    return result