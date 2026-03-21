"""
wouldn't it be nice if I could have something that
veries the same SQL code -> SQLModel code consequence
across all implementations? let's try
"""

from helpers.verify_helpers import (
    parse_verify,
    sqlite_verify,
    postgres_verify,
    verify,
    parametrize_codegens,
)


@parametrize_codegens(parse_verify, sqlite_verify, postgres_verify)
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
        rels=False,
    )