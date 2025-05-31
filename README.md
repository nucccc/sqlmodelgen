# sqlmodelgen

`sqlmodelgen` is a library to generate models for the **sqlmodel** library ([repo](https://github.com/fastapi/sqlmodel), [official docs](https://sqlmodel.tiangolo.com/)).

It accepts in input the following sources:

* direct `CREATE TABLE` sql statements
* sqlite file path
* postgres connection string

## Installation

Available on PyPi, just run `pip install sqlmodelgen`

Code generation from postgres requires the separate `postgres` extension, installable with `pip install sqlmodelgen[postgres]`

## Usage

### Generating from CREATE TABLE

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

### Generating from SQLite

```python
from sqlmodelgen import gen_code_from_sqlite

code = gen_code_from_sqlite('/home/my_user/my_database.sqlite')
```

### Generating from Postgres

The separate `postgres` extension is required, it can be installed with `pip install sqlmodelgen[postgres]`.

```python
from sqlmodelgen import gen_code_from_postgres

code = gen_code_from_postgres('postgres://USER:PASSWORD@HOST:PORT/DBNAME')
```

### Relationships

`sqlmodelgen` allows to build relationships by passing the argument `generate_relationships=True` to the functions:

* `gen_code_from_sql`
* `gen_code_from_sqlite`
* `gen_code_from_postgres`

In such case `sqlmodelgen` is going to generate relationships between classes based on the foreign keys retrieved.
The following example

```python
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

sqlmodel_code = gen_code_from_sql(schema, generate_relationships=True)
```

will generate:

```python
from sqlmodel import SQLModel, Field, Relationship

class Nations(SQLModel, table = True):
    __tablename__ = 'nations'

    id: int | None = Field(primary_key=True)
    name: str
    athletess: list['Athletes'] = Relationship(back_populates='nation')
                                                                             
class Athletes(SQLModel, table = True):
    __tablename__ = 'athletes'

    id: int | None = Field(primary_key=True)
    name: str
    nation_id: int | None = Field(foreign_key="nations.id")
    nation: Nations | None = Relationship(back_populates='athletess')
```

## Internal functioning

The library relies on [sqloxide](https://github.com/wseaton/sqloxide) to parse SQL code, then generates sqlmodel classes accordingly
