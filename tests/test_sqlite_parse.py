import sqlite3

from sqlmodelgen.ir.sqlite import sqlite_parse
from sqlmodelgen.ir.ir import SchemaIR, TableIR, ColIR


def test_collect_sqlite_ir():
    schema_ir = sqlite_parse.collect_sqlite_ir('tests/files/hero.db')

    assert schema_ir == SchemaIR(
        table_irs=[
            TableIR(
                name='hero',
                col_irs=[
                    ColIR(
                        name='id',
                        data_type='INTEGER',
                        primary_key=True,
                        not_null=True,
                        unique=False
                    ),
                    ColIR(
                        name='name',
                        data_type='VARCHAR',
                        primary_key=False,
                        not_null=True,
                        unique=False
                    ),
                    ColIR(
                        name='secret_name',
                        data_type='VARCHAR',
                        primary_key=False,
                        not_null=True,
                        unique=False
                    ),
                    ColIR(
                        name='age',
                        data_type='INTEGER',
                        primary_key=False,
                        not_null=False,
                        unique=False
                    )
                ]
            )
        ]
    )