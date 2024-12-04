'''
this module generates sqlmode code from an intermediate representation
'''


from src.ir.ir import SchemaIR, TableIR, ColIR


def gen_code(schema_ir: SchemaIR) -> str:
    code_generator = CodeGen(schema_ir)
    return code_generator.generate_code()


class CodeGen():

    def __init__(self, schema_ir: SchemaIR):
        # flag used to check if the Field class shall be imported
        self._import_field: bool = False
        self._schema_ir = schema_ir

    
    def generate_code(self) -> str:
        models_code = self._generate_models_code()
        import_code = self._generate_import_code()
        return f'{import_code}\n\n{models_code}'

    
    def _generate_models_code(self) -> str:
        table_models_code: list[str] = list()
        for table_ir in self._schema_ir.table_irs:
            table_code, used_field = gen_table_code(table_ir)
            table_models_code.append(table_code)
            if used_field:
                self._import_field = True
        return '\n\n'.join(table_models_code)
    
    
    def _generate_import_code(self):
        import_code = 'from sqlmodel import SQLModel'
        if self._import_field:
            import_code += ', Field'
        return import_code
    

def gen_table_code(table_ir: TableIR) -> tuple[str, bool]:
    used_field = False
    
    header_code = f'''class {table_ir.name}(SQLModel, table = True):
\t__tablename__ = '{table_ir.name}' '''
    
    cols_lines: list[str] = list()
    for col_ir in table_ir.col_irs:
        col_line, used_field_in_col = gen_col_line(col_ir)
        cols_lines.append(col_line)
        if used_field_in_col:
            used_field = True
    cols_code = '\n'.join(cols_lines)

    code = f'{header_code}\n{cols_code}'

    return code, used_field

def gen_col_line(col_ir: ColIR) -> tuple[str, bool]:
    used_field = False
    
    col_line = f'\t{col_ir.name}: {col_ir.data_type}'
    if not col_ir.not_null:
        col_line += ' | None'
    if col_ir.primary_key:
        col_line += ' = Field(primary_key=True)'
        used_field = True

    return col_line, used_field