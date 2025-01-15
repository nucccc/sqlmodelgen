from dataclasses import dataclass
from typing import Iterable, Iterator

from sqlmodelgen.ir.ir import TableIR

class Model:

    def __init__(self, table_ir: TableIR, class_names: set[str]):
        self.ir = table_ir
        self.class_name = gen_class_name(table_ir.name, class_names)

        self.m2o_relationships: list[Relationship] = list()
        self.o2m_relationships: list[Relationship] = list()	


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
    
def get_model_by_table_name(models: Iterable[Model], table_name: str) -> Model | None:
    for model in models:

        if model.table_name == table_name:
            return model
        
    return None


@dataclass
class Relationship:
	o2m_model: Model
	m2o_model: Model
	o2m_rel_name: str | None = None
	m2o_rel_name: str | None = None

	def determine_rel_names(self):
		# TODO: this does not guarantee that two relationships do not have the same name
		if self.m2o_rel_name is None:
			rel_name = self.o2m_model.table_name + 's'
			# i keep adding an s until the 
			while self.m2o_model.ir.get_col_ir(rel_name) is not None:
				rel_name = rel_name + 's'
			self.m2o_rel_name = rel_name
		if self.o2m_rel_name is None:
			rel_name = self.m2o_model.table_name
			while self.o2m_model.ir.get_col_ir(rel_name) is not None:
				rel_name = rel_name + 's'
			self.o2m_rel_name = rel_name
			
def arrange_relationships(model_irs: list[Model]):
    for model in model_irs:
        for col_ir in model.ir.col_irs:
            
            if col_ir.foreign_key is None:
                continue
            
            m2o_model: Model | None = get_model_by_table_name(model_irs, col_ir.foreign_key.target_table)

            if m2o_model is None:
                continue

            rel = Relationship(
				m2o_model=m2o_model,
				o2m_model=model
            )
			
            model.o2m_relationships.append(rel)
            m2o_model.m2o_relationships.append(rel)