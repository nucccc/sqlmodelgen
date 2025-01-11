from dataclasses import dataclass
from typing import Iterable, Iterator

from sqlmodelgen.ir.ir import TableIR

class Model:

    def __init__(self, table_ir: TableIR, class_names: set[str]):
        self.ir = table_ir
        self.class_name = gen_class_name(table_ir.name, class_names)

        self.relationships: list[Relationship] = list()
        self.referencing_relationships: list[Relationship] = list()	


    @property
    def table_name(self) -> str:
        return self.ir.name
    
    def iterate_attribute_names(self) -> Iterator[str]:
        for col_ir in self.ir.col_irs:
            yield col_ir.name
        # then relationships already with a name shall be there

def gen_class_name(table_name: str, class_names: set[str]) -> str:
    class_name = table_name.capitalize()
    
    while class_name in class_names:
        class_name += 'Table'

    return class_name
    
def get_model_by_table_name(models: Iterable[Model], table_name: str) -> Model:
    for model in models:

        if model.table_name == table_name:
            return model


@dataclass
class Relationship:
	listing_model: Model
	referencing_model: Model
	listing_rel_name: str | None = None
	referencing_rel_name: str | None = None

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
			
def arrange_relationships(model_irs: list[Model]):
    for model in model_irs:
        for col_ir in model.ir.col_irs:
            
            if col_ir.foreign_key is None:
                continue
            
            listing_model: Model = get_model_by_table_name(model_irs, col_ir.foreign_key.target_table)

            rel = Relationship(
				listing_model=listing_model,
				referencing_model=model
            )
			
            model.relationships.append(rel)
            listing_model.referencing_relationships.append(rel)