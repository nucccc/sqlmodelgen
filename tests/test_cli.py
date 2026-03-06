from pathlib import Path
from tempfile import tempdir

import pytest

from sqlmodelgen.cli import main_cli

def test_cli_no_source():
    with pytest.raises(SystemExit):
        main_cli([])

    with pytest.raises(SystemExit):
        main_cli(['-o', '/tmp/output.py'])

    with pytest.raises(SystemExit):
        main_cli(['-r'])

    # assert False