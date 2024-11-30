from src.ir.ir import parse_ir, ColIR

def test_collect_ir():
    schema = '''CREATE TABLE Persons (
    PersonID int NOT NULL,
    LastName varchar(255) NOT NULL,
    FirstName varchar(255) NOT NULL,
    Address varchar(255) NOT NULL,
    City varchar(255) NOT NULL
);'''

    schema_ir = parse_ir(schema)

    table_ir = schema_ir.get_table_ir('Persons')

    assert table_ir.name == 'Persons'
    assert table_ir.col_irs == [
        ColIR(
            name='PersonID',
            data_type='int',
            primary_key=False,
            nullable=False
        ),
        ColIR(
            name='LastName',
            data_type='str',
            primary_key=False,
            nullable=False
        ),
        ColIR(
            name='FirstName',
            data_type='str',
            primary_key=False,
            nullable=False
        ),
        ColIR(
            name='Address',
            data_type='str',
            primary_key=False,
            nullable=False
        ),
        ColIR(
            name='City',
            data_type='str',
            primary_key=False,
            nullable=False
        )
    ]