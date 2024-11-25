from dataclasses import dataclass
from typing import Iterable, Iterator

import sqloxide

def create_table_dict_from_parsed(parsed : list[dict]) -> dict:
	return parsed[0]['CreateTable']


@dataclass
class ColData:
	name: str
	data_type: str


not_null_option = {'name': None, 'option': 'NotNull'}


def convert_data_type(data_type_parsed, options_parsed) -> str:
	type_key = next(key for key in data_type_parsed.keys())
	result = 'any'
	if type_key == 'Int':
		result = 'int'
	if type_key == 'Varchar':
		result = 'str'
	#eventually checking options
	if options_parsed is not None and not_null_option not in options_parsed:
		result += ' | None'
	return result


def collect_cols_data(ctparsed : dict) -> Iterator[ColData]:
	cols_parsed = ctparsed['columns']
	for elem in cols_parsed:
		data_type_parsed = elem['data_type']
		options_parsed = elem['options']
		yield ColData(
			name = elem['name']['value'],
			data_type = convert_data_type(data_type_parsed, options_parsed) 
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