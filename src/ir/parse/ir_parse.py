'''
this module shall account for obtaining the actual intermediate representation
'''


from typing import Iterator

from sqloxide import parse_sql

from ir.ir import (
	ColIR,
	TableIR,
	SchemaIR,
	FKIR
)
from ir.parse.org_parse import (
	collect_column_options,
	collect_data_type,
    collect_table_contraints
)


def ir_parse(sql_code: str, dialect: str = 'generic') -> SchemaIR:
	parsed = parse_sql(sql_code, dialect)

	table_irs: list[TableIR] = list()
	for ctparsed in iter_ctparseds(parsed):
		table_irs.append(collect_table_ir(ctparsed))
	return SchemaIR(
		table_irs=table_irs
	)


def iter_ctparseds(parsed : list[dict]) -> Iterator[dict]:
	for elem in parsed:
		ctparsed = elem.get('CreateTable')
		yield ctparsed
		

def collect_table_ir(ctparsed: dict) -> TableIR:
	table_name = table_name_from_ctparsed(ctparsed)
	col_irs: list[ColIR] = list(collect_cols_data(ctparsed))
	
	constraints = collect_table_contraints(ctparsed['constraints'])
	if constraints.primary_key is not None:
		for col_ir in col_irs:
			if col_ir.name in constraints.primary_key:
				col_ir.primary_key = True

	table_ir = TableIR(
		name=table_name,
		col_irs=col_irs
	)

	# adding foreign key constraint
	if constraints.foreign_key is not None:
		for fk_constraint in constraints.foreign_key:
			col_ir = table_ir.get_col_ir(fk_constraint.column_name)

			if col_ir is None:
				continue

			col_ir.foreign_key = FKIR(
				target_table=fk_constraint.foreign_table,
				target_column=fk_constraint.foreign_column
			)

	return table_ir


def table_name_from_ctparsed(ctparsed: dict) -> str:
	return ctparsed['name'][0]['value']


def collect_cols_data(ctparsed : dict) -> Iterator[ColIR]:
	cols_parsed = ctparsed['columns']
	for col_parsed in cols_parsed:
		yield collect_col_ir(col_parsed)


def collect_col_ir(col_parsed: dict[str, any]) -> ColIR:
    name = col_parsed['name']['value']
    col_type = convert_data_type(collect_data_type(col_parsed['data_type']))
    col_options = collect_column_options(col_parsed['options'])
    return ColIR(
		name = name,
		data_type = col_type,
		primary_key = col_options.primary_key,
		not_null = col_options.not_null,
		unique=col_options.unique
	)


def convert_data_type(
	data_type_parsed
) -> str:
	if type(data_type_parsed) is dict:
		type_key = next(key for key in data_type_parsed.keys())
	else:
		type_key = data_type_parsed
	result = 'any'
	if type_key == 'Int' or type_key == 'Integer' or type_key == 'BIGSERIAL':
		result = 'int'
	if type_key == 'Varchar' or type_key == 'Text':
		result = 'str'
	if type_key == 'Boolean':
		result = 'bool'
	return result



