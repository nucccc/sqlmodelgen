'''
since the test helpers involve some untrivial operations related
to code parsing, it is actually deemed worthy to have some dedicated
tests
'''

import ast

from helpers.helpers import (
    type_data_from_ast_annassign
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