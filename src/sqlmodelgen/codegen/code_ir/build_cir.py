from sqlmodelgen.codegen.code_ir.code_ir import ModelIR
from sqlmodelgen.codegen.code_ir.build_rels import add_relationships_attrs
from sqlmodelgen.codegen.code_ir.build_col_attrs import attribute_from_col
from sqlmodelgen.codegen.code_ir.build_table_args import build_unique_constraints
from sqlmodelgen.ir.ir import SchemaIR, TableIR

def build_model_irs(schema_ir: SchemaIR, gen_relationships: bool) -> list[ModelIR]:
    class_names: set[str] = set()
    models_by_table_name: dict[str, ModelIR] = dict()

    for table_ir in schema_ir.table_irs:
        model_ir = build_model_ir(table_ir=table_ir, class_names=class_names)

        models_by_table_name[model_ir.table_name] = model_ir
        
        class_names.add(model_ir.class_name)

    if gen_relationships:
        # TODO: implement
        add_relationships_attrs(schema_ir, models_by_table_name)

    return list(models_by_table_name.values())


def gen_class_name(table_name: str, class_names: set[str]) -> str:
    class_name = table_name.capitalize()
    
    while class_name in class_names:
        class_name += 'Table'

    return class_name


    
def build_model_ir(table_ir: TableIR, class_names: set[str]) -> ModelIR:
    return ModelIR(
        class_name=gen_class_name(table_ir.name, class_names),
        table_name=table_ir.name,
        attrs=[attribute_from_col(col_ir) for col_ir in table_ir.col_irs],
        table_args=list(build_unique_constraints(table_ir)),
    )