from pathlib import Path
from tempfile import tempdir

from sqlmodelgen.cli import main_cli

def launch_cli_in_tmpfile(args: list[str]) -> str:
    '''
    this helper ensures that the cli will be launched
    having as target output -o a temporary file whose content
    will be returned by this function

    it is thus unnecessary to insert the -o args in input
    to this function
    '''
    if '-o' in args:
        raise RuntimeError('-o already present in args')

    # TODO: use a random filename generator
    tpath = Path(tempdir) / "f.py"

    main_cli(
        args
        + [
            # We must not include the header as we use non-deterministic
            # temporary filenames.
            # This makes checking the output strings a little tricky.
            # So we just ignore the header!
            '--no-header',
            '-o',
            str(tpath),
        ]
    )

    return tpath.read_text()
