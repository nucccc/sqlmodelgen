from codegen import gen_code
from ir.parse.ir_parse import ir_parse


def gen_code_from_sql(sql_code: str) -> str:
    return gen_code(ir_parse(sql_code))