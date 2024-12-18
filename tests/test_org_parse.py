import pytest

from ir.parse.org_parse import (
    collect_data_type,
    collect_column_options,
    collect_table_contraints,
    ColumnOptions,
    TableConstraints
)


def test_get_data_type():
    assert collect_data_type(
        'Text'
    ) == 'Text'

    assert collect_data_type(
        {'Int': None}
    ) == 'Int'

    assert collect_data_type(
        {'Custom': ([{'value': 'BIGSERIAL', 'quote_style': None}], [])}
    ) == 'BIGSERIAL'


def test_collect_column_option():
    assert collect_column_options(
        []
    ) == ColumnOptions(
        unique=False,
        not_null=False,
        primary_key=False
    )
    
    assert collect_column_options(
        [{'name': None, 'option': 'NotNull'}]
    ) == ColumnOptions(
        unique=False,
        not_null=True,
        primary_key=False
    )

    assert collect_column_options(
        [
            {'name': None, 'option': {
                'Unique': {'is_primary': True, 'characteristics': None}
            }}
        ]
    ) == ColumnOptions(
        unique=True,
        not_null=False,
        primary_key=True
    )

    assert collect_column_options(
        [
            {'name': None, 'option': 'NotNull'},
            {'name': None, 'option': {
                'Unique': {'is_primary': False, 'characteristics': None}
            }}
        ]
    ) == ColumnOptions(
        unique=True,
        not_null=True,
        primary_key=False
    )


def test_collect_table_contraints():
    assert collect_table_contraints(
        []
    ) == TableConstraints(
        primary_key=None
    )

    assert collect_table_contraints(
        [
            {
               'PrimaryKey':{
                  'name':None,
                  'index_name':None,
                  'index_type':None,
                  'columns':[
                     {
                        'value':'id',
                        'quote_style':None
                     }
                  ],
                  'index_options':[
                     
                  ],
                  'characteristics':None
               }
            }
        ]
    ) == TableConstraints(
        primary_key=['id']
    )