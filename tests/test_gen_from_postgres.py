'''
this test module shall verify that code generation from direct connection
with postgres works
'''

import psycopg
import docker

from sqlmodelgen import gen_code_from_postgres

from helpers.helpers import collect_code_info
from helpers.postgres_container import postgres_container
        

def test_gen_code():

    with postgres_container() as pgc:
        with psycopg.connect(pgc.get_conn_string()) as conn:
            cursor = conn.cursor()

            cursor.execute('''CREATE TABLE hero (
	id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	secret_name VARCHAR NOT NULL, 
	age INTEGER, 
	PRIMARY KEY (id)
)''')
            conn.commit()

        code_generated = gen_code_from_postgres(pgc.get_conn_string())

        assert collect_code_info(code_generated) == collect_code_info('''from sqlmodel import SQLModel, Field

class Hero(SQLModel, table = True):
\t__tablename__ = 'hero'

\tid: int = Field(primary_key=True)
\tname: str
\tsecret_name: str
\tage: int | None''')
