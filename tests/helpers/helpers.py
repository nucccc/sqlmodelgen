import ast
from dataclasses import dataclass


# then I need a portion of code to actually handle the type of a
# sqlmodel column

@dataclass
class TypeData:
    type_name: str
    optional: bool


def type_data_from_ast_annassign(
    ann_assign : ast.AnnAssign
) -> TypeData:
    return type_data_from_ast_annotation(ann_assign.annotation)


def type_data_from_ast_annotation(
    ast_node: ast.Name | ast.BinOp
) -> TypeData:
    '''
    with the limitation of assuming that the column type is either
    a name or a binary pipe "|" operation with a name and a None
    '''
    node_type = type(ast_node)
    if node_type is ast.Name:
        return TypeData(
            type_name=ast_node.id,
            optional=False
        )
    elif node_type is ast.BinOp:
        return type_data_from_binop(ast_node)
    else:
        raise TypeError
    

def type_data_from_binop(
    ast_node: ast.BinOp
) -> TypeData:
    '''
    this basically assumes that among the two terms one is a None
    '''
    # checking that the operation is actually a pipe |
    if type(ast_node.op) != ast.BitOr:
        raise ValueError

    type_name = None
    none_present = False
    
    for term in (ast_node.left, ast_node.right):
        term_type = type(term)
        if term_type is ast.Constant:
            if term.value is None:
                none_present = True
            else:
                raise ValueError
        elif term_type is ast.Name:
            type_name = term.id
    
    # checking if both a type_name and a None value constant
    # were found
    if type_name is None or not none_present:
        raise ValueError
    
    return TypeData(
        type_name=type_name,
        optional=True
    )


@dataclass
class ColumnAstInfo:
    col_name: str
    type_data: TypeData
    field_kws: dict[str, any] | None = None


@dataclass
class ClassAstInfo:
    class_name: str
    table_name: str | None
    cols_info: dict[str, ColumnAstInfo]


@dataclass
class ModuleAstInfo:
    sqlmodel_imports: set[str]
    classes_info: dict[str, ClassAstInfo]


def verify_module(
    generated_code: str,
    expected_code_info: ModuleAstInfo
) -> bool:
    code_info = collect_code_info(generated_code)

    assert code_info == expected_code_info


def collect_code_info(generated_code: str) -> ModuleAstInfo:
    ast_mod = ast.parse(generated_code)

    return mod_info_from_ast_mod(ast_mod)


def mod_info_from_ast_mod(ast_mod: ast.Module) -> ModuleAstInfo:
    sqlmodel_imports: set[str] = set()
    classes_info: dict[str, ClassAstInfo] = dict()

    for stat in ast_mod.body:
        # collecting class
        if type(stat) is ast.ClassDef:
            class_key = stat.name
            class_info = collect_sqlmodel_class(stat)

            if class_info is not None:
                classes_info[class_key] = class_info
        
        # collecting the imports
        if type(stat) is ast.ImportFrom:
            sqlmodel_imports = sqlmodel_imports.union(collect_sqlmodel_imports(stat))


    return ModuleAstInfo(
        sqlmodel_imports=sqlmodel_imports,
        classes_info=classes_info
    )


def collect_sqlmodel_imports(stat: ast.ImportFrom) -> set[str]:
    # in case the module is not sqlmodel just return
    if stat.module != 'sqlmodel':
        return {}
    
    sqlmodel_imports: set[str] = {
        alias.name
        for alias in stat.names
    }

    return sqlmodel_imports


def collect_sqlmodel_class(class_def: ast.ClassDef) -> ClassAstInfo | None:
    '''
    this function ensures that SQLModel is among the bases and that
    table == True is there, otherwise it just returns None
    '''
    if not is_valid_sqlmodel_class(class_def):
        return None

    class_name = class_def.name
    table_name: str | None = None
    cols_info: dict[str, ColumnAstInfo] = dict()
    
    for stat in class_def.body:
        # trying to collect the table name from the assignment
        if type(stat) is ast.Assign:
            candidate_table_name = collect_table_name(stat)
            if candidate_table_name is None:
                continue 
            table_name = candidate_table_name
        elif type(stat) is ast.AnnAssign:
            col_info = collect_col_info(stat)
            cols_info[col_info.col_name] = col_info

    return ClassAstInfo(
        class_name=class_name,
        table_name=table_name,
        cols_info=cols_info
    )


def collect_col_info(stat: ast.AnnAssign) -> ColumnAstInfo:
    type_data = type_data_from_ast_annassign(stat)

    # collecting eventual field keywords
    fields_kws = collect_field_kws(stat)

    return ColumnAstInfo(
        col_name=stat.target.id,
        type_data=type_data,
        field_kws=fields_kws
    )

def collect_field_kws(stat: ast.AnnAssign) -> dict[str, any] | None:
    if stat.value is None:
        return None
    
    call: ast.Call = stat.value
    if type(call) is not ast.Call:
        return None

    return {
        kw.arg: kw.value.value
        for kw in call.keywords
    }


def collect_table_name(stat: ast.Assign) -> str | None:
    if len(stat.targets) != 1:
        return None
    target = stat.targets[0]
    if type(target) is not ast.Name:
        return None
    if target.id != '__tablename__':
        return None
    if type(stat.value) is not ast.Constant:
        return None
    return stat.value.value


def is_valid_sqlmodel_class(class_def: ast.ClassDef) -> bool:
    # ensuring that the class inherits from 'SQLModel'
    for base in class_def.bases:
        if type(base) is ast.Name and base.id == 'SQLModel':
            break
    else:
        return False
    
    # ensuring that table=True is provided among the keywords
    for kw in class_def.keywords:
        if kw.arg == 'table' and type(kw.value) is ast.Constant and kw.value.value == True:
            break
    else:
        return False

    return True