# sqlmodelgen

`sqlmodelgen` is a library to convert `CREATE TABLE` statements from SQL to classes inheriting `SQLModel` from the famous [sqlmodel library](https://sqlmodel.tiangolo.com/).

At the moment there is support (with limites capabilities) for direct interconnection with SQLite and Postgres

## Example

```python
from sqlmodelgen import gen_code_from_sql

sql_code = '''
CREATE TABLE Hero (
	id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	secret_name VARCHAR NOT NULL, 
	age INTEGER, 
	PRIMARY KEY (id)
);

print(gen_code_from_sql(sql_code))
'''
```

generates:

```python
from sqlmodel import SQLModel, Field

class Hero(SQLModel, table = True):
    __tablename__ = 'Hero'
    id: int = Field(primary_key=True)
    name: str
    secret_name: str
    age: int | None
```

## Installation

It is already published on PyPi, just type `pip install sqlmodelgen`

 Code generation from postgres requires the separate `postgres` extension, installable with `pip install sqlmodelgen[postgres]`

## Internal functioning

The library relies on [sqloxide](https://github.com/wseaton/sqloxide) to parse SQL code, then generates sqlmodel classes accordingly

## Possible improvements

- Support for more SQL data types