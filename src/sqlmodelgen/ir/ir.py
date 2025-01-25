from dataclasses import dataclass


not_null_option = {'name': None, 'option': 'NotNull'}


@dataclass
class FKIR:
	'''
	FKIR is the foreign key intermediate representation
	'''
	target_table: str
	target_column: str


@dataclass
class ColIR:
	name: str
	data_type: str
	primary_key: bool
	not_null: bool
	unique: bool
	default: any = None
	foreign_key: FKIR | None = None


@dataclass
class TableIR:
	name: str
	col_irs: list[ColIR]

	def get_col_ir(self, name: str) -> ColIR | None:
		for col_ir in self.col_irs:
			if col_ir.name == name:
				return col_ir
		return None
	

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
