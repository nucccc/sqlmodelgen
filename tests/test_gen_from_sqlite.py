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
