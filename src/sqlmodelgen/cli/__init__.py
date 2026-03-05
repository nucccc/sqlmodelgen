'''
here there shall be code to actually have the cli
'''
import argparse
import sys
from pathlib import Path


from sqlmodelgen import gen_code_from_sql, gen_code_from_sqlite
from sqlmodelgen.utils.dependency_checker import check_postgres_deps, check_mysql_deps
from sqlmodelgen.utils.mysql_parse import parse_mysql


def main_cli(args=None):
    parser = _build_parser()
    args = parser.parse_args(args)

    _act_on_args(args, parser)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='sqlmodelgen',
        description='sqlmodel classes code generation',
    )

    # Mutually exclusive input sources
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-f', '--file', type=Path, help='SQL file path')
    input_group.add_argument('-s', '--sqlite', type=Path, help='SQLite database path')
    input_group.add_argument('-p', '--postgres', type=str, help='PostgreSQL connection URL')
    input_group.add_argument('-m', '--mysql', type=str, help='MySQL connection URL')

    # Additional options
    parser.add_argument('-o', '--output', type=Path, help='Output file (default: stdout)')
    parser.add_argument('-r', '--relationships', action='store_true', help='Generate relationships')
    parser.add_argument('--schema', type=str, default='public', help='PostgreSQL schema (default: public)')
    parser.add_argument('--dbname', type=str, help='MySQL database name (required with --mysql)')

    return parser


def _act_on_args(args: argparse.Namespace, usage: str):
    # Validation: --mysql requires --dbname
    if args.mysql and not args.dbname:
        _exit('--dbname is required when using --mysql', usage)

    # Generate code based on input source
    if args.file:
        sql_code = args.file.read_text()
        output = gen_code_from_sql(sql_code, generate_relationships=args.relationships)

    elif args.sqlite:
        output = gen_code_from_sqlite(str(args.sqlite), generate_relationships=args.relationships)

    elif args.postgres:
        if not check_postgres_deps():
            sys.exit('PostgreSQL support requires psycopg. Please install with: pip install sqlmodelgen[postgres]')
        from sqlmodelgen import gen_code_from_postgres
        output = gen_code_from_postgres(args.postgres, schema_name=args.schema, generate_relationships=args.relationships)

    elif args.mysql:
        if not check_mysql_deps():
            sys.exit('MySQL support requires mysql-connector-python. Please install with: pip install sqlmodelgen[mysql]')
        from mysql import connector
        from sqlmodelgen import gen_code_from_mysql

        try:
            mysql_info = parse_mysql(args.mysql)
        except Exception as e:
            _exit(str(e))

        with connector.connect(
            host=mysql_info.host,
            port=mysql_info.port,
            user=mysql_info.user,
            password=mysql_info.psw
        ) as conn:
            output = gen_code_from_mysql(
                conn=conn,
                dbname=args.dbname,
                generate_relationships=args.relationships,
            )
    else:
        # This should never happen due to required=True on the mutually exclusive group
        _exit('No input source specified', usage)

    # Output result
    if args.output:
        args.output.write_text(output)
    else:
        print(output)


def _exit(error: str, usage: str | None = None):
    if usage:
        print(usage)
    sys.exit(error)
