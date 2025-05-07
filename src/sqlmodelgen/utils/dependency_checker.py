def check_postgres_deps() -> bool:
    try:
        import psycopg
    except ImportError:
        return False
    return True