from subprocess import call

import pytest

from bocadillo import __version__
from bocadillo.cli import create_cli


def test_can_call_boca():
    assert call(["boca"]) == 0


@pytest.mark.parametrize("flag", ["-v", "-V", "--version", "version"])
def test_get_version(runner, flag):
    cli = create_cli()

    result = runner.invoke(cli, [flag])
    assert result.exit_code == 0
    assert __version__ in result.output
