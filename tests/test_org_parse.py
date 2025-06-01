from sqlmodelgen.ir.parse.org_parse import (
    collect_column_options,
    collect_table_contraints,
    collect_foreign_table_name,
    ColumnOptions,
    TableConstraints
)


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


def test_foreign_table_name():
    # testing for ct_parsed formats, either before and after sqloxide
    # version 0.1.56 introducing Identifier
    assert collect_foreign_table_name(
        {'value':'hero'}
    ) == 'hero'

    assert collect_foreign_table_name(
        {'Identifier':{'value':'hero'}}
    ) == 'hero'
