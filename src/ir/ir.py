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


@dataclass
class SchemaIR:
	table_irs: list[TableIR]

	def get_table_ir(self, name: str) -> TableIR | None:
		'''
		get_table_ir returns the intermediate representation of a table
		given a name
		'''
		for table_ir in self.table_irs:
			if table_ir.name != name:
				continue
			return table_ir
		return None


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


def iter_ctparseds(parsed : list[dict]) -> Iterator[dict]:
	for elem in parsed:
		ctparsed = elem.get('CreateTable')
		yield ctparsed


def ctparsed_from_parsed(parsed : list[dict]) -> dict:
	return parsed[0]['CreateTable']


def parse_ir(schema: str, dialect: str = 'generic') -> SchemaIR:
	parsed = parse_sql(schema, dialect)

	table_irs: list[TableIR] = list()
	for ctparsed in iter_ctparseds(parsed):
		table_irs.append(collect_ir(ctparsed))
	return SchemaIR(
		table_irs=table_irs
	)


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
