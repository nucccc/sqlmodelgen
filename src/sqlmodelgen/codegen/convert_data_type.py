'''
this module shall account for the conversion of data types from sql to python
'''

# TODO: types for datetimes, requires to import the actual datetime in the end

INT_TYPES = {
	'int',
	'integer',
	'smallserial',
	'serial',
	'bigserial',
	'int',
	'tinyint',
	'smallint',
	'mediumint',
	'bigint'
}

FLOAT_TYPES = {
	'float',
	'double',
	'double precision',
	'decimal',
	'dec',
	'numeric',
	'real',
	'single'
}

STR_TYPES = {
	'varchar',
	'text',
	'tinytext',
	'mediumtext',
	'longtext',
	'character varying',
}

BOOL_TYPES = {
	'boolean',
	'bool'
}

BYTES_TYPES = {
	'blob',
	'tinyblob',
	'mediumblob',
	'longblob'
}

UUID_TYPES = {
	'uuid'
}

DATETIME_TYPES = {
	'timestamp',
	'timestamp with time zone',
}

def convert_data_type(
	data_type: str
) -> str:
	data_type = data_type.lower()
	result = 'any'
	if data_type in INT_TYPES:
		result = 'int'
	elif data_type in FLOAT_TYPES:
		result = 'float'
	elif data_type in STR_TYPES:
		result = 'str'
	elif data_type in BOOL_TYPES:
		result = 'bool'
	elif data_type in BYTES_TYPES:
		result = 'bytes'
	elif data_type in UUID_TYPES:
		result = 'UUID'
	elif data_type in DATETIME_TYPES:
		result = 'datetime'
	return result