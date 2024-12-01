import pytest

from src.ir.parse.org_parse import (
    get_data_type
)


def test_get_data_type():
    assert get_data_type(
        'Text'
    ) == 'Text'

    assert get_data_type(
        {'Int': None}
    ) == 'Int'

    assert get_data_type(
        {'Custom': ([{'value': 'BIGSERIAL', 'quote_style': None}], [])}
    ) == 'BIGSERIAL'