from .codegen.codegen import gen_code
from .ir.parse.ir_parse import ir_parse
from .ir.sqlite.sqlite_parse import collect_sqlite_ir
from .utils.dependency_checker import check_postgres_deps


def gen_code_from_sql(sql_code: str, generate_relationships: bool = False) -> str:
    return gen_code(ir_parse(sql_code), generate_relationships)

if check_postgres_deps():
    from .ir.postgres.postgres_collect import collect_postgres_ir
    def gen_code_from_postgres(
        postgres_conn_addr: str,
        schema_name: str = 'public',
        generate_relationships: bool = False
    ) -> str:
        return gen_code(
            schema_ir=collect_postgres_ir(postgres_conn_addr, schema_name),
            generate_relationships=generate_relationships
        )

def gen_code_from_sqlite(
    sqlite_address: str,
    generate_relationships: bool = False
) -> str:
    return gen_code(
        collect_sqlite_ir(sqlite_address),
        generate_relationships=generate_relationships
    )
