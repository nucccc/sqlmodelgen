import pytest

from sqlmodelgen import gen_code

def test_sqlmodelgen():
    schema = '''CREATE TABLE Persons (
    PersonID int,
    LastName varchar(255),
    FirstName varchar(255),
    Address varchar(255),
    City varchar(255)
);'''

    assert gen_code(schema) == '''from sqlmodel import SQLModel

class Persons(SQLModel, table = True):
	PersonID: int
	LastName: str
	FirstName: str
	Address: str
	City: str'''