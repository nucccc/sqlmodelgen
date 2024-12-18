from ir.ir import ColIR
from ir.parse.ir_parse import ir_parse

def test_collect_ir():
    schema = '''CREATE TABLE Persons (
    PersonID int NOT NULL,
    LastName varchar(255) NOT NULL,
    FirstName varchar(255) NOT NULL,
    Address varchar(255) NOT NULL,
    City varchar(255) NOT NULL
);'''

    schema_ir = ir_parse(schema)

    table_ir = schema_ir.get_table_ir('Persons')

    assert table_ir.name == 'Persons'
    assert table_ir.col_irs == [
        ColIR(
            name='PersonID',
            data_type='int',
            primary_key=False,
            not_null=True,
            unique=False
        ),
        ColIR(
            name='LastName',
            data_type='str',
            primary_key=False,
            not_null=True,
            unique=False
        ),
        ColIR(
            name='FirstName',
            data_type='str',
            primary_key=False,
            not_null=True,
            unique=False
        ),
        ColIR(
            name='Address',
            data_type='str',
            primary_key=False,
            not_null=True,
            unique=False
        ),
        ColIR(
            name='City',
            data_type='str',
            primary_key=False,
            not_null=True,
            unique=False
        )
    ]


def test_2_unrelated_tables():
    sql = '''
CREATE TABLE users(
    id BIGSERIAL NOT NULL,
    PRIMARY KEY (id),
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    psw_hash TEXT NOT NULL
);

CREATE TABLE leagues(
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    public BOOLEAN
);
'''
    schema_ir = ir_parse(sql, dialect='postgres')

    users_ir = schema_ir.get_table_ir('users')
    assert users_ir.name == 'users'
    assert users_ir.col_irs == [
        ColIR(
            name='id',
            data_type='int',
            primary_key=True,
            not_null=True,
            unique=False
        ),
        ColIR(
            name='email',
            data_type='str',
            primary_key=False,
            not_null=True,
            unique=True
        ),
        ColIR(
            name='name',
            data_type='str',
            primary_key=False,
            not_null=True,
            unique=False
        ),
        ColIR(
            name='psw_hash',
            data_type='str',
            primary_key=False,
            not_null=True,
            unique=False
        )
    ]

    leagues_ir = schema_ir.get_table_ir('leagues')
    assert leagues_ir.name == 'leagues'
    assert leagues_ir.col_irs == [
        ColIR(
            name='id',
            data_type='int',
            primary_key=True,
            not_null=False,
            unique=True
        ),
        ColIR(
            name='name',
            data_type='str',
            primary_key=False,
            not_null=True,
            unique=True
        ),
        ColIR(
            name='public',
            data_type='bool',
            primary_key=False,
            not_null=False,
            unique=False
        )
    ]