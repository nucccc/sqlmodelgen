import pytest

import ast
from dataclasses import dataclass

from src.ir.ir import SchemaIR, TableIR, ColIR
from src.codegen import CodeGen, gen_table_code, gen_code

from helpers.helpers import collect_code_info


def test_gen_table_code():
    table_code, used_field = gen_table_code(
        TableIR(
            name='a_table',
            col_irs=[
                ColIR(
                    name='id',
                    data_type='int',
                    primary_key=True,
                    not_null=False,
                    unique=True
                ),
                ColIR(
                    name='name',
                    data_type='str',
                    primary_key=False,
                    not_null=True,
                    unique=True
                ),
                ColIR(
                    name='email',
                    data_type='str',
                    primary_key=False,
                    not_null=False,
                    unique=True
                ),
            ]
        )
    )

    # asserting that the function actually generated a field
    assert used_field == True

    generated_code_info = collect_code_info(table_code)

    expected_code_info = collect_code_info('''class a_table(SQLModel, table = True):
    __tablename__ = 'a_table'
    id: int | None = Field(primary_key=True)
    name: str
    email: str | None
''')
    
    assert generated_code_info == expected_code_info


def test_gen_code():
    generated_code = gen_code(
        SchemaIR(
            table_irs=[
                TableIR(
                    name='a_table',
                    col_irs=[
                        ColIR(
                            name='id',
                            data_type='int',
                            primary_key=True,
                            not_null=False,
                            unique=True
                        ),
                        ColIR(
                            name='name',
                            data_type='str',
                            primary_key=False,
                            not_null=True,
                            unique=True
                        ),
                        ColIR(
                            name='email',
                            data_type='str',
                            primary_key=False,
                            not_null=False,
                            unique=True
                        ),
                    ]
                )
            ]
        )
    )

    generated_code_info = collect_code_info(generated_code)

    expected_code_info = collect_code_info(
        '''from sqlmodel import SQLModel, Field

class a_table(SQLModel, table = True):
    __tablename__ = 'a_table'
    id: int | None = Field(primary_key=True)
    name: str
    email: str | None'''
    )

    assert generated_code_info == expected_code_info
