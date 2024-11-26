from dataclasses import dataclass
from typing import Iterator

from sqloxide import parse_sql


not_null_option = {'name': None, 'option': 'NotNull'}


@dataclass
class ColIR:
    name: str
    data_type: str
    primary_key: bool
    nullable: bool


@dataclass
class TableIR:
    name: str
    col_irs: list[ColIR]


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


def ctparsed_from_parsed(parsed : list[dict]) -> dict:
	return parsed[0]['CreateTable']


def parse_ir(schema: str, dialect: str = 'generic') -> TableIR:
    parsed = parse_sql(schema, dialect)
    ctparsed = ctparsed_from_parsed(parsed)
    return collect_ir(ctparsed)


def table_name_from_ctparsed(ctparsed: dict) -> str:
	return ctparsed['name'][0]['value']


def convert_data_type(
	data_type_parsed
) -> str:
	type_key = next(key for key in data_type_parsed.keys())
	result = 'any'
	if type_key == 'Int' or type_key == 'Integer':
		result = 'int'
	if type_key == 'Varchar':
		result = 'str'
	return result


def collect_cols_data(ctparsed : dict) -> Iterator[ColIR]:
	primary_key_column_name = get_primary_key(ctparsed)
	cols_parsed = ctparsed['columns']
	for elem in cols_parsed:
		name = elem['name']['value']
		data_type_parsed = elem['data_type']
		options_parsed = elem['options']
		yield ColIR(
			name = name,
			data_type = convert_data_type(data_type_parsed),
			primary_key = primary_key_column_name == name,
			nullable = options_parsed is None or not_null_option not in options_parsed
		)


def collect_ir(ctparsed: dict) -> TableIR:
    table_name = table_name_from_ctparsed(ctparsed)
    col_irs: list[ColIR] = list(collect_cols_data(ctparsed))
    return TableIR(
		name=table_name,
		col_irs=col_irs
    )
