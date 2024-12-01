from dataclasses import dataclass
from typing import Iterator

from sqloxide import parse_sql


not_null_option = {'name': None, 'option': 'NotNull'}


@dataclass
class ColIR:
	name: str
	data_type: str
	primary_key: bool
	not_null: bool
	unique: bool


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


