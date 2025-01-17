from sqlmodelgen.ir.parse.ir_parse import collect_data_type

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