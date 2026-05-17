'''
since the test helpers involve some untrivial operations related
to code parsing, it is actually deemed worthy to have some dedicated
tests
'''

import ast

from helpers.helpers import (
    type_data_from_ast_annassign,
    collect_code_info,
    collect_schema_name_table_arg,
    ModuleAstInfo,
    ClassAstInfo,
    ColumnAstInfo,
    TypeData
)


def test_type_data_from_ast_annassign():
    ann_assign = ast.parse('var_name: int').body[0]
    type_data = type_data_from_ast_annassign(ann_assign)
    assert type_data.type_name == 'int'
    assert type_data.optional == False

    ann_assign = ast.parse('var_name: int | None').body[0]
    type_data = type_data_from_ast_annassign(ann_assign)
    assert type_data.type_name == 'int'
    assert type_data.optional == True

    ann_assign = ast.parse('var_name: None | int').body[0]
    type_data = type_data_from_ast_annassign(ann_assign)
    assert type_data.type_name == 'int'
    assert type_data.optional == True


def test_collect_code_info():

    code_info = collect_code_info('''from datetime import datetime
from datetime import date
from sqlmodel import SQLModel, Field, UniqueConstraint

class a_table(SQLModel, table = True):
    __tablename__ = 'a_table'
    __table_args__ = (
        UniqueConstraint('name'),
        {'schema':'a_schema'},
    )
    id: int | None = Field(primary_key=True)
    name: str
    email: str | None''')

    assert code_info == ModuleAstInfo(
        imports_from={
            'datetime':{'datetime', 'date'},
            'sqlmodel':{'SQLModel', 'Field', 'UniqueConstraint'}
        },
        classes_info={
            'a_table': ClassAstInfo(
                class_name='a_table',
                table_name='a_table',
                uniques={('name', )},
                cols_info={
                    'id':ColumnAstInfo(
                        col_name='id',
                        type_data=TypeData(
                            type_name='int',
                            optional=True
                        ),
                        field_kws={
                            'primary_key':True
                        }
                    ),
                    'name':ColumnAstInfo(
                        col_name='name',
                        type_data=TypeData(
                            type_name='str',
                            optional=False
                        )
                    ),
                    'email':ColumnAstInfo(
                        col_name='email',
                        type_data=TypeData(
                            type_name='str',
                            optional=True
                        )
                    ),
                },
                schema_name_arg='a_schema',
            )
        }
    )

def test_collect_schema_info():
    '''
    this test shall assert that the schema name is
    collected successfully if present in different types of table args
    '''

    # declaring code with several SQLModel classes, all with
    # different or non existing __table_args__
    table_arg_only_schema_info = collect_code_info('''
class a_table(SQLModel, table = True):
    __tablename__ = 'a_table'
    __table_args__ = {'schema':'a_schema'}
    id: int | None = Field(primary_key=True)
    name: str

class b_table(SQLModel, table = True):
    __tablename__ = 'b_table'
    __table_args__ = ({'schema':'b_schema'},)
    id: int | None = Field(primary_key=True)
    name: str

class c_table(SQLModel, table = True):
    __tablename__ = 'c_table'
    __table_args__ = (UniqueConstraint('name'),{'schema':'c_schema'},)
    id: int | None = Field(primary_key=True)
    name: str

class d_table(SQLModel, table = True):
    __tablename__ = 'd_table'
    __table_args__ = (UniqueConstraint('name'),)
    id: int | None = Field(primary_key=True)
    name: str

class e_table(SQLModel, table = True):
    __tablename__ = 'e_table'
    id: int | None = Field(primary_key=True)
    name: str
''')

    # out of the collected code info a dictionary associating
    # to every table name is built
    schema_names_dict = {
        class_name : class_info.schema_name_arg
        for class_name, class_info in table_arg_only_schema_info.classes_info.items()
    }

    assert schema_names_dict == {
        'a_table':'a_schema',
        'b_table':'b_schema',
        'c_table':'c_schema',
        'd_table':None,
        'e_table':None,
    }


def test_collect_schema_name_table_arg():
    expr = ast.parse('{\'schema\' : \'another_schema\'}', mode='eval')
    assert collect_schema_name_table_arg(expr.body) == 'another_schema'

    expr = ast.parse('(\'schema\', \'another_schema\')', mode='eval')
    assert collect_schema_name_table_arg(expr.body) is None

    expr = ast.parse('2 + 2', mode='eval')
    assert collect_schema_name_table_arg(expr.body) is None

    expr = ast.parse('2 + 2', mode='eval')
    assert collect_schema_name_table_arg(expr.body) is None