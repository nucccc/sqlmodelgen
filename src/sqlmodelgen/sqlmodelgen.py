from .codegen.codegen import gen_code
from .ir.parse.ir_parse import ir_parse


def gen_code_from_sql(sql_code: str, generate_relationships: bool = False) -> str:
    return gen_code(ir_parse(sql_code), generate_relationships)