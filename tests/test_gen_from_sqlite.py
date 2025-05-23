import sqlite3

from sqlmodelgen import gen_code_from_sqlite

from helpers.helpers import collect_code_info


def test_gen_code_from_sqlite():
    code_generated = gen_code_from_sqlite('tests/files/hero.db')

    assert collect_code_info(code_generated) == collect_code_info('''from sqlmodel import SQLModel, Field

class Hero(SQLModel, table = True):
\t__tablename__ = 'hero'

\tid: int = Field(primary_key=True)
\tname: str
\tsecret_name: str
\tage: int | None''')


def test_gen_code_with_fks(tmpdir):
    #determining the path of the temporary file
    fpath = tmpdir / 'fk.id'

    # creating the table in the temporary file

    with sqlite3.connect(fpath) as conn:
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE nations(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )''')

        cursor.execute('''CREATE TABLE athletes(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            nation_id BIGSERIAL NOT NULL,
            FOREIGN KEY (nation_id) REFERENCES nations(id)
        )''')

        conn.commit()

    # testing code generation with relationships

    code_generated_with_rels = gen_code_from_sqlite(fpath, generate_relationships=True)

    assert collect_code_info(code_generated_with_rels) == collect_code_info('''from sqlmodel import SQLModel, Field, Relationship

class Nations(SQLModel, table=True):
    __tablename__ = 'nations'
    id: int | None = Field(primary_key=True)
    name: str
    athletess: list['Athletes'] = Relationship(back_populates='nation')

class Athletes(SQLModel, table=True):
    __tablename__ = 'athletes'
    id: int | None = Field(primary_key=True)
    name: str
    nation_id: int = Field(foreign_key='nations.id')
    nation: 'Nations' | None = Relationship(back_populates='athletess')''')

    # testing code generation without relationships

    code_generated_without_rels = gen_code_from_sqlite(fpath, generate_relationships=False)

    assert collect_code_info(code_generated_without_rels) == collect_code_info('''from sqlmodel import SQLModel, Field

class Nations(SQLModel, table=True):
    __tablename__ = 'nations'
    id: int | None = Field(primary_key=True)
    name: str

class Athletes(SQLModel, table=True):
    __tablename__ = 'athletes'
    id: int | None = Field(primary_key=True)
    name: str
    nation_id: int = Field(foreign_key='nations.id')''')
    