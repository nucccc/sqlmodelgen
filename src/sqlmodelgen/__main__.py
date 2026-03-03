import argparse
import sys
from pathlib import Path

from .sqlmodelgen import gen_code_from_sql, gen_code_from_sqlite
from .utils.dependency_checker import check_postgres_deps, check_mysql_deps


def main():
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

    args = parser.parse_args()

    # Validation: --mysql requires --dbname
    if args.mysql and not args.dbname:
        parser.error('--dbname is required when using --mysql')

    # Generate code based on input source
    if args.file:
        sql_code = args.file.read_text()
        output = gen_code_from_sql(sql_code, generate_relationships=args.relationships)

    elif args.sqlite:
        output = gen_code_from_sqlite(str(args.sqlite), generate_relationships=args.relationships)

    elif args.postgres:
        if not check_postgres_deps():
            sys.exit('PostgreSQL support requires psycopg. Install with: pip install sqlmodelgen[postgres]')
        from .sqlmodelgen import gen_code_from_postgres
        output = gen_code_from_postgres(args.postgres, schema_name=args.schema, generate_relationships=args.relationships)

    elif args.mysql:
        if not check_mysql_deps():
            sys.exit('MySQL support requires mysql-connector-python. Install with: pip install sqlmodelgen[mysql]')
        # TODO: Handle MySQL connection from URL string
        sys.exit('MySQL support not yet fully implemented in CLI')

    else:
        # This should never happen due to required=True on the mutually exclusive group
        parser.error('No input source specified')

    # Output result
    if args.output:
        args.output.write_text(output)
    else:
        print(output)


if __name__ == '__main__':
    main()