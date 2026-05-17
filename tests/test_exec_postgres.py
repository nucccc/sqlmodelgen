'''
this test shall somehow execute the python code generated against a real postgres database
'''

import psycopg
import pytest
from sqlmodel import SQLModel

from sqlmodelgen import gen_code_from_postgres
from helpers.postgres_container import postgres_container


@pytest.fixture(autouse=True)
def reset_sqlmodel():
    '''
    this hereby implemented fixture is used to reset the metadata,
    i.e. the data regarding the declared SQLModel classes
    representing the tables. In this way several tests interfacing
    with different database instances can regenerate different
    tables with the same name
    '''
    yield
    # drops table objects
    SQLModel.metadata.clear()


def test_exec_single_schema_name_with_uniques():
    '''
    verifies that a table in a schema with uniques can be
    actually inserted and then selected rows
    '''

    sql = '''CREATE SCHEMA IF NOT EXISTS user_data;
    
CREATE TABLE user_data.users(
    id uuid NOT NULL,
    PRIMARY KEY (id),
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE,
    psw TEXT NOT NULL
);
'''

    with postgres_container() as pgc:
        conn_str = pgc.get_conn_string()
        with psycopg.connect(conn_str) as conn:
            # creating schema and tables with cursor
            cursor = conn.cursor()
            if isinstance(sql, str):
                cursor.execute(sql)
            elif isinstance(sql, list):
                for statement in sql:
                    cursor.execute(statement)
            conn.commit()

            # generating code
            generated_code = gen_code_from_postgres(
                postgres_conn_addr=conn_str,
                schema_name='user_data',
            )

            # support_code is the code to be executed against
            # the existing database, in order to verify the actual
            # code's functionality to interact with the database
            support_code = f'''

from sqlmodel import Session, create_engine, select

conn_str = conn_str.replace('postgres', 'postgresql+psycopg')
engine = create_engine(conn_str, echo=False)

with Session(engine) as session:


    hero = Users(
        name='Robin',
        email='robin@waine_ind.com',
        psw='bruceWayneBoomer'
    )
    session.add(hero)
    session.commit()

    heroes = session.exec(select(Users)).all()

    assert len(heroes) == 1
    assert heroes[0].name == 'Robin'
    assert heroes[0].psw == 'bruceWayneBoomer'
'''
            exec_code = generated_code + support_code

            print(exec_code)

            exec(exec_code, locals())


def test_exec_single_schema_name_without_uniques():
    '''
    verifies that a table in a schema without uniques can be
    actually inserted and selected rows
    '''

    sql = '''CREATE SCHEMA IF NOT EXISTS user_data;
    
CREATE TABLE user_data.users(
    id uuid NOT NULL,
    PRIMARY KEY (id),
    email TEXT NOT NULL,
    name TEXT NOT NULL,
    psw TEXT NOT NULL
);
'''

    with postgres_container() as pgc:
        conn_str = pgc.get_conn_string()
        with psycopg.connect(conn_str) as conn:
            # creating schema and tables with cursor
            cursor = conn.cursor()
            if isinstance(sql, str):
                cursor.execute(sql)
            elif isinstance(sql, list):
                for statement in sql:
                    cursor.execute(statement)
            conn.commit()

            # generating code
            generated_code = gen_code_from_postgres(
                postgres_conn_addr=conn_str,
                schema_name='user_data',
            )

            # support_code is the code to be executed against
            # the existing database, in order to verify the actual
            # code's functionality to interact with the database
            support_code = f'''

from sqlmodel import Session, create_engine, select

conn_str = conn_str.replace('postgres', 'postgresql+psycopg')
engine = create_engine(conn_str, echo=False)

with Session(engine) as session:


    hero = Users(
        name='Robin',
        email='robin@waine_ind.com',
        psw='bruceWayneBoomer'
    )
    session.add(hero)
    session.commit()

    heroes = session.exec(select(Users)).all()

    assert len(heroes) == 1
    assert heroes[0].name == 'Robin'
    assert heroes[0].psw == 'bruceWayneBoomer'
'''
            exec_code = generated_code + support_code

            print(exec_code)

            exec(exec_code, locals())