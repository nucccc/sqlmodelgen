from src.sqlmodelgen import gen_code_from_sql

from helpers.helpers import collect_code_info


# TODO: i need to test unique
# TODO: testing unique when declared as separated constraint


def test_simple_table():
    '''
    testing the code generation for a single table
    '''

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


def test_nullable():
    '''
    testing the possibility of optional types
    '''

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


def test_primary_key_separate_constraint():
    '''
    testing the case in which the primary key is declared as
    a separate constraint
    '''

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


def test_unique_single_column():

    sql = '''CREATE TABLE Hero (
	id INTEGER PRIMARY KEY NOT NULL, 
	name VARCHAR NOT NULL, 
	secret_name VARCHAR NOT NULL UNIQUE, 
	age INTEGER
);'''

    assert collect_code_info(gen_code_from_sql(sql)) == collect_code_info('''from sqlmodel import SQLModel, Field, UniqueConstraint

class Hero(SQLModel, table = True):
\t__tablename__ = 'Hero'
\t__table_args__ = [UniqueConstraint('secret_name')]

\tid: int = Field(primary_key=True)
\tname: str
\tsecret_name: str
\tage: int | None''')


def test_datetime():

    sql = '''CREATE TABLE ts (
	id INTEGER PRIMARY KEY NOT NULL, 
	dt TIMESTAMP WITH TIME ZONE
);'''

    assert collect_code_info(gen_code_from_sql(sql)) == collect_code_info('''from datetime import datetime
from sqlmodel import SQLModel, Field

class Ts(SQLModel, table = True):
\t__tablename__ = 'ts'

\tid: int = Field(primary_key=True)
\tdt: datetime | None''')


def test_foreign_key():
    '''
    testing the case of a foreign key, without relationships
    '''

    schema = '''CREATE TABLE nations(
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE athletes(
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    nation_id BIGSERIAL,
    FOREIGN KEY (nation_id) REFERENCES nations(id)
);'''

    assert collect_code_info(gen_code_from_sql(schema)) == collect_code_info('''from sqlmodel import SQLModel, Field

class Nations(SQLModel, table = True):
\t__tablename__ = 'nations'

\tid: int | None = Field(primary_key=True)
\tname: str
                                                                             
class Athletes(SQLModel, table = True):
\t__tablename__ = 'athletes'

\tid: int | None = Field(primary_key=True)
\tname: str
\tnation_id: int | None = Field(foreign_key="nations.id")''')


def test_foreign_key_and_relationship():
    '''
    testing the case of a foreign key, with the generation
    of relationships
    '''

    schema = '''CREATE TABLE nations(
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE athletes(
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    nation_id BIGSERIAL,
    FOREIGN KEY (nation_id) REFERENCES nations(id)
);'''

    assert collect_code_info(gen_code_from_sql(schema, True)) == collect_code_info('''from sqlmodel import SQLModel, Field, Relationship

class Nations(SQLModel, table = True):
\t__tablename__ = 'nations'

\tid: int | None = Field(primary_key=True)
\tname: str
\tathletess: list['Athletes'] = Relationship(back_populates='nation')
                                                                             
class Athletes(SQLModel, table = True):
\t__tablename__ = 'athletes'

\tid: int | None = Field(primary_key=True)
\tname: str
\tnation_id: int | None = Field(foreign_key="nations.id")
\tnation: Nations | None = Relationship(back_populates='athletess')''')


def test_foreign_key_missing_table():
    '''
    testing when the foreign table does not exist
    '''

    schema = '''CREATE TABLE athletes(
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    nation_id BIGSERIAL,
    FOREIGN KEY (nation_id) REFERENCES nations(id)
);'''

    assert collect_code_info(gen_code_from_sql(schema)) == collect_code_info('''from sqlmodel import SQLModel, Field

class Athletes(SQLModel, table = True):
\t__tablename__ = 'athletes'

\tid: int | None = Field(primary_key=True)
\tname: str
\tnation_id: int | None = Field(foreign_key="nations.id")''')
    

def test_foreign_key_and_relationship_missing_table():    
    schema = '''CREATE TABLE athletes(
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    nation_id BIGSERIAL,
    FOREIGN KEY (nation_id) REFERENCES nations(id)
);'''

    assert collect_code_info(gen_code_from_sql(schema, True)) == collect_code_info('''from sqlmodel import SQLModel, Field

class Athletes(SQLModel, table = True):
\t__tablename__ = 'athletes'

\tid: int | None = Field(primary_key=True)
\tname: str
\tnation_id: int | None = Field(foreign_key="nations.id")''')


def test_foreign_key_and_relationship_same_name():
    '''
    testing the case of a foreign key, with the name
    '''

    schema = '''CREATE TABLE table1(
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE table2(
    id BIGSERIAL PRIMARY KEY,
    f TEXT NOT NULL,
    f_id BIGSERIAL,
    FOREIGN KEY (f_id) REFERENCES table1(id)
);'''

    assert collect_code_info(gen_code_from_sql(schema, True)) == collect_code_info('''from sqlmodel import SQLModel, Field, Relationship

class Table1(SQLModel, table = True):
\t__tablename__ = 'table1'

\tid: int | None = Field(primary_key=True)
\tname: str
\ttable2s: list['Table2'] = Relationship(back_populates='f_rel')
                                                                             
class Table2(SQLModel, table = True):
\t__tablename__ = 'table2'

\tid: int | None = Field(primary_key=True)
\tf: str
\tf_id: int | None = Field(foreign_key="table1.id")
\tf_rel: Table1 | None = Relationship(back_populates='table2s')''')
