from typing import Iterator

from mysql.connector.connection_cext import CMySQLConnection
from mysql.connector.cursor_cext import CMySQLCursor

from sqlmodelgen.ir.ir import (
	ColIR,
	TableIR,
	SchemaIR,
	FKIR
)
from sqlmodelgen.ir.query import ColQueryData, ContraintsData, ir_build

class MySQLCollector:

	def __init__(
		self,
		cnx: CMySQLConnection,
		dbname: str,
	):
		self.cnx = cnx
		self.dbname = dbname


	def collect_table_names(self) -> Iterator[str]:
		cur = self.cnx.cursor()
		yield from collect_tables(cur, self.dbname)


	def collect_columns(self, table_name: str) -> Iterator[ColQueryData]:
		cur = self.cnx.cursor()
		yield from collect_columns(cur, self.dbname, table_name)


	def collect_constraints(self) -> ContraintsData:
		cur = self.cnx.cursor()

		uniques = collect_uniques(cur, self.dbname)
		primary_keys = collect_primary_keys(cur, self.dbname)
		foreign_keys = collect_foreign_keys(cur, self.dbname)

		return ContraintsData(
			uniques=uniques,
			primary_keys=primary_keys,
			foreign_keys=foreign_keys,
		)


def collect_mysql_ir(cnx: CMySQLConnection, dbname: str) -> SchemaIR:
	return ir_build(collector=MySQLCollector(
		cnx=cnx,
		dbname=dbname
	))


def collect_columns(
	cur: CMySQLCursor,
	schema_name: str,
	table_name: str,
) -> Iterator[ColQueryData]:
	cur.execute(f'''SELECT
		COLUMN_NAME,
		ORDINAL_POSITION,
		IS_NULLABLE,
		DATA_TYPE,
		COLUMN_TYPE
	FROM
		information_schema.COLUMNS
	WHERE
		TABLE_SCHEMA = '{schema_name}'
		AND TABLE_NAME = '{table_name}'
	ORDER BY
		TABLE_NAME,
		ORDINAL_POSITION;''')

	for col_name, ord_pos, is_nullable, data_type, col_type in cur.fetchall():
		yield ColQueryData(
			name=col_name,
			data_type=data_type,
			is_nullable=is_nullable=='YES'
		)


def collect_tables(cur: CMySQLCursor, schema_name: str) -> Iterator[str]:
	cur.execute(f'''SELECT
		TABLE_NAME
	FROM
		information_schema.TABLES
	WHERE
		TABLE_SCHEMA = '{schema_name}'
	ORDER BY
		TABLE_NAME;''')

	for elem in cur.fetchall():
		yield elem[0]


def collect_uniques(
	cur: CMySQLCursor,
	schema_name: str,
):
	cur.execute('''SELECT
		tc.TABLE_SCHEMA,
		tc.TABLE_NAME,
		tc.CONSTRAINT_NAME,
		kcu.COLUMN_NAME
	FROM
		information_schema.TABLE_CONSTRAINTS tc
	JOIN
		information_schema.KEY_COLUMN_USAGE kcu
		ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
		AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
		AND tc.TABLE_NAME = kcu.TABLE_NAME
	WHERE
		tc.CONSTRAINT_TYPE = 'UNIQUE'
	ORDER BY
		tc.TABLE_SCHEMA,
		tc.TABLE_NAME,
		kcu.ORDINAL_POSITION;''')
	
	result: dict[str, set[str]] = dict()
	
	for table_schema, table_name, constraint_name, column_name in cur.fetchall():
		if table_schema != schema_name:
			continue

		if table_name not in result.keys():
			result[table_name] = set()

		result[table_name].add(column_name)

	return result


def collect_primary_keys(
	cur: CMySQLCursor,
	schema_name: str,
) -> dict[str, set[str]]:
	cur.execute(f'''SELECT
		TABLE_NAME,
		COLUMN_NAME
	FROM
		information_schema.KEY_COLUMN_USAGE
	WHERE
		CONSTRAINT_NAME = 'PRIMARY'
		AND TABLE_SCHEMA = '{schema_name}'
	ORDER BY
		TABLE_SCHEMA,
		TABLE_NAME,
		ORDINAL_POSITION;''')

	result: dict[str, set[str]] = dict()
	
	for table_name, col_name in cur.fetchall():
		if table_name not in result.keys():
			result[table_name] = set()

		result[table_name].add(col_name)

	return result


def collect_foreign_keys(
	cur: CMySQLCursor,
	schema_name: str,
) -> dict[str, dict[str, FKIR]]:
	cur.execute(f'''SELECT
		kcu.TABLE_SCHEMA,
		kcu.TABLE_NAME,
		kcu.CONSTRAINT_NAME,
		kcu.COLUMN_NAME,
		kcu.REFERENCED_TABLE_SCHEMA,
		kcu.REFERENCED_TABLE_NAME,
		kcu.REFERENCED_COLUMN_NAME
	FROM
		information_schema.KEY_COLUMN_USAGE kcu
	JOIN
		information_schema.TABLE_CONSTRAINTS tc
		ON kcu.CONSTRAINT_NAME = tc.CONSTRAINT_NAME
		AND kcu.TABLE_SCHEMA = tc.TABLE_SCHEMA
		AND kcu.TABLE_NAME = tc.TABLE_NAME
	WHERE
		tc.CONSTRAINT_TYPE = 'FOREIGN KEY'
		AND kcu.TABLE_SCHEMA = '{schema_name}'
		AND kcu.REFERENCED_TABLE_SCHEMA = '{schema_name}'
	ORDER BY
		kcu.TABLE_SCHEMA,
		kcu.TABLE_NAME,
		kcu.ORDINAL_POSITION;''')
	
	result: dict[str, dict[str, FKIR]] = dict()
	
	for (
		table_schema,
		table_name,
		constraint_name,
		column_name,
		referenced_table_schema,
		referenced_table_name,
		referenced_column_name,
	) in cur.fetchall():
		table_fks = result.get(table_name)
		if table_fks is None:
			table_fks = dict()
			result[table_name] = table_fks

		table_fks[column_name] = FKIR(
			target_table=referenced_table_name,
			target_column=referenced_column_name
		)

	return result