from dataclasses import dataclass
from typing import Iterable, Iterator

import sqloxide

def create_table_dict_from_parsed(parsed : list[dict]) -> dict:
	return parsed[0]['CreateTable']


def get_primary_key(ctparsed : dict) -> str | None:
	'''
	get_primary_key returns the name of the column representing the primary key,
	of course it assumes that only a single column is going to be the primary key
	'''
	constraints = ctparsed.get('constraints')
	if not constraints:
		return None
	for constraint in constraints:
		if type(constraint) != dict:
			continue
		primary_key = constraint.get('PrimaryKey')
		if type(primary_key) != dict:
			continue
		return primary_key['columns'][0]['value']
	return None


@dataclass
class ColData:
	name: str
	data_type: str


not_null_option = {'name': None, 'option': 'NotNull'}


def convert_data_type(
	data_type_parsed,
	options_parsed,
	is_primary_key: bool
) -> str:
	type_key = next(key for key in data_type_parsed.keys())
	result = 'any'
	if type_key == 'Int' or type_key == 'Integer':
		result = 'int'
	if type_key == 'Varchar':
		result = 'str'
	#eventually checking options
	if is_primary_key or (options_parsed is not None and not_null_option not in options_parsed):
		result += ' | None'
	return result


def collect_cols_data(ctparsed : dict) -> Iterator[ColData]:
	primary_key_column_name = get_primary_key(ctparsed)
	cols_parsed = ctparsed['columns']
	for elem in cols_parsed:
		name = elem['name']['value']
		data_type_parsed = elem['data_type']
		options_parsed = elem['options']
		yield ColData(
			name = name,
			data_type = convert_data_type(data_type_parsed, options_parsed, primary_key_column_name == name) 
		)


def gen_col_code(col_data: ColData) -> str:
	return f'\t{col_data.name}: {col_data.data_type}'


def gen_cols_code(cols_data: Iterable[ColData]) -> str:
	return '\n'.join(gen_col_code(col_data) for col_data in cols_data)


def gen_sqlmodel_code(table_name: str, cols_data: Iterable[ColData]) -> str:
	return f'''from sqlmodel import SQLModel

class {table_name}(SQLModel, table = True):
{gen_cols_code(cols_data)}'''


def codegen_from_parsed(ctparsed : dict) -> str:
	table_name = ctparsed['name'][0]['value']
	cols_data = list(collect_cols_data(ctparsed))
	return gen_sqlmodel_code(table_name, cols_data)


def gen_code(sql_schema: str) -> str:
    parsed = sqloxide.parse_sql(sql_schema, dialect='generic')
    
    return codegen_from_parsed(create_table_dict_from_parsed(parsed))