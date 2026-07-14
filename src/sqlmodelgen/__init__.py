import importlib.metadata

from .sqlmodelgen import (
    gen_code_from_sql as gen_code_from_sql,
    gen_code_from_sqlite as gen_code_from_sqlite,
)

from .utils.dependency_checker import check_postgres_deps, check_mysql_deps

if check_postgres_deps():
    from .sqlmodelgen import gen_code_from_postgres as gen_code_from_postgres

if check_mysql_deps():
    from .sqlmodelgen import gen_code_from_mysql as gen_code_from_mysql


__version__ = importlib.metadata.version('sqlmodelgen')
