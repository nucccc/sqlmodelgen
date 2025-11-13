from dataclasses import dataclass
from typing import Iterable, Iterator, Protocol

from sqlmodelgen.ir.ir import (
	ColIR,
	TableIR,
	SchemaIR,
	FKIR
)

@dataclass
class ColQueryData:
    name: str
    data_type: str
    is_nullable: bool = True

@dataclass
class ContraintsData:
    uniques: dict[str, set[str]]
    primary_keys: dict[str, set[str]]
    foreign_keys: dict[str, dict[str, FKIR]]

    def is_unique(self, table_name: str, column_name: str) -> bool:
        return column_name in self.uniques.get(table_name, set())
    
    def is_primary_key(self, table_name: str, column_name: str) -> bool:
        return column_name in self.primary_keys.get(table_name, set())
    
    def get_foreign_key(self, table_name: str, column_name: str) -> FKIR | None:
        table_fks = self.foreign_keys.get(table_name)

        if table_fks is None:
            return None
        
        return table_fks.get(column_name)

class QCollector(Protocol):
    '''
    a protocol for collection of stuff from sql, that is which a sql collector shall satisfy
    '''

    def collect_table_names(self) -> Iterator[str]:
        pass

    def collect_columns(self, table_name: str) -> Iterator[ColQueryData]:
        pass

    def collect_constraints(self) -> ContraintsData:
        pass


def ir_build(collector: QCollector) -> SchemaIR:
    constraints = collector.collect_constraints()

    tables_names = list(collector.collect_table_names())

    table_irs: list[TableIR] = list()
    for table_name in tables_names:
        cols_data = collector.collect_columns(table_name)

        table_irs.append(TableIR(
            name=table_name,
            col_irs=list(build_cols_ir(
                cols_data=cols_data,
                table_name=table_name,
                constraints=constraints,
            ))
        ))

    return SchemaIR(
        table_irs=table_irs
    )

def build_cols_ir(
    cols_data: Iterable[ColQueryData],
    table_name: str,
    constraints: ContraintsData
) -> Iterator[ColIR]:
    for col_data in cols_data:
        # TODO: a lot of ORs here for new constraints coming from structure, no?
        # in theory what arrives from the constraints should have priority I guess
        yield ColIR(
            name=col_data.name,
            data_type=col_data.data_type,
            primary_key=constraints.is_primary_key(table_name, col_data.name),
            not_null=not col_data.is_nullable, # TODO: handle this into a bool
            unique=constraints.is_unique(table_name, col_data.name),
            foreign_key=constraints.get_foreign_key(table_name, col_data.name)
        )