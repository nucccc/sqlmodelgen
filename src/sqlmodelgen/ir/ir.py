from dataclasses import dataclass, field
from typing import Iterator

from sqloxide import parse_sql


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
class RelationshipIR:
	main_table: TableIR
	foreign_table: TableIR
	rel_name: str | None = None
	foreign_rel_name: str | None = None

	def determine_rel_names(self):
		# TODO: this does not guarantee that two relationships do not have the same name
		if self.rel_name is None:
			rel_name = self.foreign_table.name + 's'
			# i keep adding an s until the 
			while self.main_table.get_col_ir(rel_name) is not None:
				rel_name = rel_name + 's'
			self.rel_name = rel_name
		if self.foreign_rel_name is None:
			foreign_rel_name = self.main_table.name
			while self.foreign_table.get_col_ir(foreign_rel_name) is not None:
				foreign_rel_name = foreign_rel_name + 's'
			self.foreign_rel_name = foreign_rel_name


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


	def arrange_relationships(self):
		'''
		this given the tables' foreign keys I hope can
		'''
		for table_ir in self.table_irs:
			for col_ir in table_ir.col_irs:
				if col_ir.foreign_key is None:
					continue

				main_table = self.get_table_ir(col_ir.foreign_key.target_table)

				rel_ir = RelationshipIR(
					main_table=main_table,
					foreign_table=table_ir
				)

				table_ir.foreign_relationships.append(rel_ir)
				main_table.relationships.append(rel_ir)