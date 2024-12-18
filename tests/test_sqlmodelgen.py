"""import pytest

from src.sqlmodelgen import gen_code_from_sql


def test_sqlmodelgen():
    schema = '''CREATE TABLE Persons (
    PersonID int NOT NULL,
    LastName varchar(255) NOT NULL,
    FirstName varchar(255) NOT NULL,
    Address varchar(255) NOT NULL,
    City varchar(255) NOT NULL
);'''

    assert gen_code_from_sql(schema) == '''from sqlmodel import SQLModel

class Persons(SQLModel, table = True):
	PersonID: int
	LastName: str
	FirstName: str
	Address: str
	City: str'''


def test_sqlmodelgen_nullable():
    schema = '''CREATE TABLE Persons (
    PersonID int NOT NULL,
    LastName varchar(255) NOT NULL,
    FirstName varchar(255) NOT NULL,
    Address varchar(255),
    City varchar(255)
);'''

    assert gen_code_from_sql(schema) == '''from sqlmodel import SQLModel

class Persons(SQLModel, table = True):
	PersonID: int
	LastName: str
	FirstName: str
	Address: str | None
	City: str | None'''

def test_sqlmodelgen_primary_key():
    schema = '''CREATE TABLE Hero (
	id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	secret_name VARCHAR NOT NULL, 
	age INTEGER, 
	PRIMARY KEY (id)
);'''

    assert gen_code_from_sql(schema) == '''from sqlmodel import SQLModel

class Hero(SQLModel, table = True):
\tid: int | None
\tname: str
\tsecret_name: str
\tage: int | None'''"""