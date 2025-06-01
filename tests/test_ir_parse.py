from sqlmodelgen.ir.parse.ir_parse import (
    table_name_from_ctparsed,
    collect_data_type
)


def test_table_name_from_ctparsed():
    # testing for ct_parsed formats, either before and after sqloxide
    # version 0.1.56 introducing Identifier
    assert table_name_from_ctparsed(
        {'name':[{'value':'hero'}]}
    ) == 'hero'

    assert table_name_from_ctparsed(
        {'name':[{'Identifier':{'value':'hero'}}]}
    ) == 'hero'


def test_collect_data_type():
    assert collect_data_type('Text') == 'Text'
    assert collect_data_type('Boolean') == 'Boolean'
    assert collect_data_type({'Int': None}) == 'Int'
    assert collect_data_type(
        {'Varchar': {'IntegerLength': {'length': 255, 'unit': None}}}
    ) == 'Varchar'
    assert collect_data_type(
        {'Custom': ([{'quote_style': None, 'value': 'BIGSERIAL'}], [])}
    ) == 'BIGSERIAL'