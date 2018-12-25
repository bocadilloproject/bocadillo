from subprocess import call

import pytest

from bocadillo import __version__
from bocadillo.cli import create_cli


@pytest.mark.parametrize("command", [["boca"], ["python", "-m", "bocadillo"]])
def test_invoke_boca(command):
    assert call(command) == 0


@pytest.mark.parametrize("flag", ["-v", "-V", "--version", "version"])
def test_get_version(runner, flag):
    cli = create_cli()

    result = runner.invoke(cli, [flag])
    assert result.exit_code == 0
    assert __version__ in result.output
