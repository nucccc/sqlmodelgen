from sqlmodelgen.codegen.convert_data_type import convert_data_type


def test_convert_data_type():
    assert convert_data_type('UNKNOWN_TYPE') == 'any'
    
    assert convert_data_type('BLOB') == 'bytes'
    assert convert_data_type('blob') == 'bytes'
    
    assert convert_data_type('INTEGER') == 'int'
    assert convert_data_type('SERIAL') == 'int'
    assert convert_data_type('BIGSERIAL') == 'int'

    assert convert_data_type('FLOAT') == 'float'
    assert convert_data_type('DECIMAL') == 'float'
    assert convert_data_type('NUMERIC') == 'float'
    assert convert_data_type('REAL') == 'float'

    assert convert_data_type('VARCHAR') == 'str'
    assert convert_data_type('TEXT') == 'str'

    assert convert_data_type('BOOLEAN') == 'bool'
    assert convert_data_type('BOOL') == 'bool'

    assert convert_data_type('UUID') == 'UUID'

    assert convert_data_type('TIMESTAMP WITH TIME ZONE') == 'datetime'
