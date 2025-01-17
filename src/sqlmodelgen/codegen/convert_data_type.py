def convert_data_type(
	data_type: str
) -> str:	
	result = 'any'
	if data_type == 'Int' or data_type == 'Integer' or data_type == 'BIGSERIAL':
		result = 'int'
	if data_type == 'Varchar' or data_type == 'Text':
		result = 'str'
	if data_type == 'Boolean':
		result = 'bool'
	return result