from src.sqlmodelgen import gen_code_from_sql

from helpers.helpers import collect_code_info


def test_sqlmodelgen():
    schema = '''CREATE TABLE Persons (
    PersonID int NOT NULL,
    LastName varchar(255) NOT NULL,
    FirstName varchar(255) NOT NULL,
    Address varchar(255) NOT NULL,
    City varchar(255) NOT NULL
);'''

    assert collect_code_info(gen_code_from_sql(schema)) == collect_code_info('''from sqlmodel import SQLModel

class Persons(SQLModel, table = True):
    __tablename__ = 'Persons'

    PersonID: int
    LastName: str
    FirstName: str
    Address: str
    City: str''')


def test_sqlmodelgen_nullable():
    schema = '''CREATE TABLE Persons (
    PersonID int NOT NULL,
    LastName varchar(255) NOT NULL,
    FirstName varchar(255) NOT NULL,
    Address varchar(255),
    City varchar(255)
);'''

    assert collect_code_info(gen_code_from_sql(schema)) == collect_code_info('''from sqlmodel import SQLModel

class Persons(SQLModel, table = True):
    __tablename__ = 'Persons'

    PersonID: int
    LastName: str
    FirstName: str
    Address: str | None
    City: str | None''')

def test_sqlmodelgen_primary_key():
    schema = '''CREATE TABLE Hero (
	id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	secret_name VARCHAR NOT NULL, 
	age INTEGER, 
	PRIMARY KEY (id)
);'''

    assert collect_code_info(gen_code_from_sql(schema)) == collect_code_info('''from sqlmodel import SQLModel, Field

class Hero(SQLModel, table = True):
\t__tablename__ = 'Hero'

\tid: int = Field(primary_key=True)
\tname: str
\tsecret_name: str
\tage: int | None''')