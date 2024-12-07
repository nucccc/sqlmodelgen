import ast
from dataclasses import dataclass

# TODO: this code validation data could have some unit testing... down the road
@dataclass
class ClassAstParse:
    class_name: str
    private_table_name: str | None
    #class_lines: list[ast.AST]
    class_cols: list[ast.AnnAssign]


@dataclass
class ModuleAstParse:
    sqlmodel_imports: set[str]
    classes_parses: list[ClassAstParse]


def verify_module(
    generated_code: str,
    expected_code_data: ModuleAstParse
) -> bool:
    return True


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