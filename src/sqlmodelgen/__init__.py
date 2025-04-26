from .sqlmodelgen import (
    gen_code_from_sql,
    gen_code_from_sqlite,
)

from .utils.dependency_checker import check_postgres_deps

if check_postgres_deps():
    from .sqlmodelgen import (
        gen_code_from_postgres
    )