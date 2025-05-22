'''
since the test helpers involve some untrivial operations related
to code parsing, it is actually deemed worthy to have some dedicated
tests
'''

import ast

from helpers.helpers import (
    type_data_from_ast_annassign,
    collect_code_info,
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
from sqlmodel import SQLModel, Field, UniqueConstraint

class a_table(SQLModel, table = True):
    __tablename__ = 'a_table'
    __table_args__ = [UniqueConstraint('name')]
    id: int | None = Field(primary_key=True)
    name: str
    email: str | None''')

    assert code_info == ModuleAstInfo(
        imports_from={
            'datetime':{'datetime'},
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
                }
            )
        }
    )
