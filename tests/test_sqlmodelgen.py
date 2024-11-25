import pytest

from src.sqlmodelgen import gen_code


def test_sqlmodelgen():
    schema = '''CREATE TABLE Persons (
    PersonID int NOT NULL,
    LastName varchar(255) NOT NULL,
    FirstName varchar(255) NOT NULL,
    Address varchar(255) NOT NULL,
    City varchar(255) NOT NULL
);'''

    assert gen_code(schema) == '''from sqlmodel import SQLModel

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

    assert gen_code(schema) == '''from sqlmodel import SQLModel

class Persons(SQLModel, table = True):
	PersonID: int
	LastName: str
	FirstName: str
	Address: str | None
	City: str | None'''