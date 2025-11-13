def check_postgres_deps() -> bool:
    try:
        import psycopg
    except ImportError:
        return False
    return True


def check_mysql_deps() -> bool:
    try:
        import mysql.connector
    except ImportError:
        return False
    return True
