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


def test_sqlmodelgen_foreign_key():
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


def test_sqlmodelgen_foreign_key_and_relationship():
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
\tathletess: list['Athletes'] = Relationship(back_populates='nations')
                                                                             
class Athletes(SQLModel, table = True):
\t__tablename__ = 'athletes'

\tid: int | None = Field(primary_key=True)
\tname: str
\tnation_id: int | None = Field(foreign_key="nations.id")
\tnations: Nations | None = Relationship(back_populates='athletess')''')


def test_sqlmodelgen_foreign_key_missing_table():
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
    

def test_sqlmodelgen_foreign_key_and_relationship_missing_table():
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
