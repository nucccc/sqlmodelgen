'''
wouldn't it be nice if I could have something that
veries the same SQL code -> SQLModel code consequence
across all implementations? let's try
'''

import sqlite3
from pathlib import Path
from tempfile import tempdir
from typing import Callable

import pytest
import psycopg
from uuid import uuid4

from sqlmodelgen import (
    gen_code_from_mysql,
    gen_code_from_postgres,
    gen_code_from_sql,
    gen_code_from_sqlite,
)

from helpers.cli_helpers import launch_cli_in_tmpfile
from helpers.helpers import collect_code_info
from helpers.mysql_container import mysql_docker
from helpers.postgres_container import postgres_container

CodeGenFunc = Callable[[str, bool], str]

def parse_verify(sql: str, rels: bool) -> str:
    # preparinf the temp file for the cli
    fpath = Path(tempdir) / f"{uuid4()}.sql"
    fpath.write_text(sql)

    func_code = gen_code_from_sql(sql, rels)
    short_arg_cli_code = _parse_cli(fpath, rels, True)
    long_arg_cli_code = _parse_cli(fpath, rels, False)

    assert func_code == short_arg_cli_code
    assert func_code == long_arg_cli_code

    return func_code


def _parse_cli(fpath: Path, rels: bool, short_arg: bool = False) -> str:
    args = [
        '-f' if short_arg else '--file',
        str(fpath),
    ]

    if rels:
        args.append('-r')

    return launch_cli_in_tmpfile(args=args)


def sqlite_verify(sql: str, rels: bool) -> str:
    # TODO: prepare interface for possibly several sql
    # statements
    sqlite_path = Path(tempdir) / f"{uuid4()}.sqlite"

    with sqlite3.connect(sqlite_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()

    func_code = gen_code_from_sqlite(str(sqlite_path), rels)
    short_arg_cli_code = _sqlite_cli(sqlite_path, rels, True)
    long_arg_cli_code = _sqlite_cli(sqlite_path, rels, False)

    assert func_code == short_arg_cli_code
    assert func_code == long_arg_cli_code

    return func_code

def _sqlite_cli(sqlite_path: Path, rels: bool, short_arg: bool = False) -> str:
    args = [
        '-s' if short_arg else '--sqlite',
        str(sqlite_path),
    ]

    if rels:
        args.append('-r')

    return launch_cli_in_tmpfile(args=args)

def postgres_verify(sql: str, rels: bool, schema_name: str = 'public') -> str:
    with postgres_container() as pgc:
        with psycopg.connect(pgc.get_conn_string()) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()

        # generating code from function
        func_code = gen_code_from_postgres(
            postgres_conn_addr=pgc.get_conn_string(),
            schema_name=schema_name,
            generate_relationships=rels,
        )

        short_arg_cli_code = _postres_cli(
            conn_string=pgc.get_conn_string(),
            rels=rels,
            schema_name=schema_name,
            short_arg=True
        )

        long_arg_cli_code = _postres_cli(
            conn_string=pgc.get_conn_string(),
            rels=rels,
            schema_name=schema_name,
            short_arg=False
        )

        # verifying all code matches
        assert func_code == short_arg_cli_code
        assert func_code == long_arg_cli_code

        return func_code
    
def _postres_cli(
    conn_string: str,
    rels: bool,
    schema_name: str = 'public',
    short_arg: bool = False
) -> str:
    
    args = [
        '-p' if short_arg else '--postgres',
        conn_string,
    ]

    if rels:
        args.append('-r')

    if schema_name != 'public':
        args.append('--schema')
        args.append(schema_name)

    return launch_cli_in_tmpfile(args=args)


def mysql_verify(sql: str, rels: bool, dbname: str = 'testdb') -> str:
    with mysql_docker() as (mysqld, conn):
        cur = conn.cursor()

        sqls = [sql]

        cur.execute(f'CREATE DATABASE IF NOT EXISTS {dbname}')

        cur.execute(f'USE {dbname}')

        for sql in sqls:
            cur.execute(sql)

        conn.commit()

        func_code = gen_code_from_mysql(conn, dbname)

        # TODO: get the connection string to invoke the cli

    return func_code


codegens: list[CodeGenFunc] = [
    parse_verify,
    sqlite_verify,
    postgres_verify,
#    mysql_verify,
]
codegen_ids = [codegen.__name__ for codegen in codegens]

def verify(codegen: CodeGenFunc, sql: str, expected: str, rels: bool):
    generated = codegen(sql, rels)
    assert collect_code_info(generated) == collect_code_info(expected)


@pytest.mark.parametrize("codegen", codegens, ids=codegen_ids)
def test_basic(codegen):
    verify(
        codegen=codegen,
        sql='''CREATE TABLE people (
    person_id int NOT NULL,
    last_name varchar NOT NULL,
    first_name varchar NOT NULL,
    address varchar,
    city varchar NOT NULL
);''',
        expected='''from sqlmodel import SQLModel

class People(SQLModel, table = True):
    __tablename__ = 'people'

    person_id: int
    last_name: str
    first_name: str
    address: str | None
    city: str''',
        rels=False
    )