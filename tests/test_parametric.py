'''
wouldn't it be nice if I could have something that
veries the same SQL code -> SQLModel code consequence
across all implementations? let's try
'''

import sqlite3
from pathlib import Path
from tempfile import tempdir
from typing import Callable

from uuid import uuid4

from sqlmodelgen import (
    gen_code_from_sql,
    gen_code_from_sqlite,
)

from helpers.helpers import collect_code_info

CodeGenFunc = Callable[[str, bool], str]

def gen_from_parse(sql: str, rels: bool) -> str:
    return gen_code_from_sql(sql, rels)

def gen_from_sqlite(sql: str, rels: bool) -> str:
    # TODO: prepare interface for possibly several sql
    # statements
    sqlite_path = Path(tempdir) / f"{uuid4()}.sqlite"

    with sqlite3.connect(sqlite_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()

    return gen_code_from_sqlite(str(sqlite_path), rels)

codegens: list[CodeGenFunc] = [
    gen_from_parse,
    gen_from_sqlite,
]
codegen_ids = [codegen.__name__ for codegen in codegens]

def verify(codegen: CodeGenFunc, sql: str, expected: str, rels: bool):
    generated = codegen(sql, rels)
    assert collect_code_info(generated) == collect_code_info(expected)

import pytest
@pytest.mark.parametrize("codegen", codegens, ids=codegen_ids)
def test_basic(codegen):
    verify(
        codegen=codegen,
        sql='''CREATE TABLE Persons (
    PersonID int NOT NULL,
    LastName varchar NOT NULL,
    FirstName varchar NOT NULL,
    Address varchar NOT NULL,
    City varchar NOT NULL
);''',
        expected='''from sqlmodel import SQLModel

class Persons(SQLModel, table = True):
    __tablename__ = 'Persons'

    PersonID: int
    LastName: str
    FirstName: str
    Address: str
    City: str''',
        rels=False
    )