import pytest

import ast
from dataclasses import dataclass

from sqlmodelgen.ir.ir import SchemaIR, TableIR, ColIR, FKIR
from sqlmodelgen.codegen.codegen import gen_code

from helpers.helpers import collect_code_info


def test_gen_code():
    generated_code = gen_code(
        SchemaIR(
            table_irs=[
                TableIR(
                    name='a_table',
                    col_irs=[
                        ColIR(
                            name='id',
                            data_type='Int',
                            primary_key=True,
                            not_null=False,
                            unique=True
                        ),
                        ColIR(
                            name='name',
                            data_type='Text',
                            primary_key=False,
                            not_null=True,
                            unique=True
                        ),
                        ColIR(
                            name='email',
                            data_type='Text',
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

class A_table(SQLModel, table = True):
    __tablename__ = 'a_table'
    id: int | None = Field(primary_key=True)
    name: str
    email: str | None'''
    )

    assert generated_code_info == expected_code_info


def test_gencode_with_foreign_key():

    generated_code = gen_code(
        SchemaIR(
            table_irs=[
                TableIR(
                    name='table1',
                    col_irs=[
                        ColIR(
                            name='id',
                            data_type='Int',
                            primary_key=True,
                            not_null=False,
                            unique=True
                        ),
                        ColIR(
                            name='name',
                            data_type='Varchar',
                            primary_key=False,
                            not_null=True,
                            unique=True
                        )
                    ]
                ),
                TableIR(
                    name='table2',
                    col_irs=[
                        ColIR(
                            name='id',
                            data_type='Int',
                            primary_key=True,
                            not_null=False,
                            unique=True
                        ),
                        ColIR(
                            name='fid',
                            data_type='Int',
                            primary_key=False,
                            not_null=False,
                            unique=False,
                            foreign_key=FKIR(
                                target_table='table1',
                                target_column='id'
                            )
                        )
                    ]
                )
            ]
        )
    )

    generated_code_info = collect_code_info(generated_code)

    expected_code_info = collect_code_info(
        '''from sqlmodel import SQLModel, Field

class Table1(SQLModel, table = True):
    __tablename__ = 'table1'
    id: int | None = Field(primary_key=True)
    name: str
    
class Table2(SQLModel, table = True):
    __tablename__ = 'table2'
    id: int | None = Field(primary_key=True)
    fid: int | None = Field(foreign_key="table1.id")'''
    )

    assert generated_code_info == expected_code_info


def test_gen_code():
    schema_ir = SchemaIR(
        table_irs=[
            TableIR(
                name='table0',
                col_irs=[
                    ColIR(
                        name='id',
                        data_type='Int',
                        primary_key=True,
                        not_null=True,
                        unique=True
                    ),
                    ColIR(
                        name='username',
                        data_type='Text',
                        primary_key=False,
                        not_null=True,
                        unique=True
                    )
                ]
            )
        ]
    )

    sqlmodel_code = gen_code(schema_ir)

    print(sqlmodel_code)

    #assert False

def test_gencode_with_relationships():

    generated_code = gen_code(
        SchemaIR(
            table_irs=[
                TableIR(
                    name='table1',
                    col_irs=[
                        ColIR(
                            name='id',
                            data_type='BIGSERIAL',
                            primary_key=True,
                            not_null=False,
                            unique=True
                        ),
                        ColIR(
                            name='name',
                            data_type='Text',
                            primary_key=False,
                            not_null=True,
                            unique=True
                        )
                    ]
                ),
                TableIR(
                    name='table2',
                    col_irs=[
                        ColIR(
                            name='id',
                            data_type='BIGSERIAL',
                            primary_key=True,
                            not_null=False,
                            unique=True
                        ),
                        ColIR(
                            name='fid',
                            data_type='Integer',
                            primary_key=False,
                            not_null=False,
                            unique=False,
                            foreign_key=FKIR(
                                target_table='table1',
                                target_column='id'
                            )
                        )
                    ]
                )
            ]
        ),
        generate_relationships=True
    )

    print(generated_code)

    generated_code_info = collect_code_info(generated_code)

    expected_code_info = collect_code_info(
        '''from sqlmodel import SQLModel, Field, Relationship

class Table1(SQLModel, table = True):
	__tablename__ = 'table1' 
	id: int | None = Field(primary_key=True)
	name: str
	table2s: list['Table2'] = Relationship(back_populates='table1')

class Table2(SQLModel, table = True):
	__tablename__ = 'table2' 
	id: int | None = Field(primary_key=True)
	fid: int | None = Field(foreign_key="table1.id")
	table1: 'Table1' | None = Relationship(back_populates='table2s')'''
    )

    assert generated_code_info == expected_code_info