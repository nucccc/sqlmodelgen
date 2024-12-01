import pytest

from src.ir.parse.org_parse import (
    collect_data_type,
    collect_column_options,
    ColumnOptions
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
        not_null=False
    )
    
    assert collect_column_options(
        [{'name': None, 'option': 'NotNull'}]
    ) == ColumnOptions(
        unique=False,
        not_null=True
    )

    assert collect_column_options(
        [
            {"name": None, "option": {
                "Unique": {"is_primary": False, "characteristics": None}
            }}
        ]
    ) == ColumnOptions(
        unique=True,
        not_null=False
    )

    assert collect_column_options(
        [
            {"name": None, "option": "NotNull"},
            {"name": None, "option": {
                "Unique": {"is_primary": False, "characteristics": None}
            }}
        ]
    ) == ColumnOptions(
        unique=True,
        not_null=True
    )