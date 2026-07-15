from sqlmodelgen.cli import main_cli

def main():
    import sys
    # Tweaks argv so `/Users/user/...etc/sqlmodelgen` is not shown
    main_cli(sys.argv[1:])


if __name__ == '__main__':
    main()
