from inspect import cleandoc

import pytest

from bocadillo.cli import create_cli
from tests.utils import env


def test_can_init_custom_commands(runner, tmpdir):
    cli = create_cli()

    result = runner.invoke(cli, ["init:custom", "-d", str(tmpdir)])

    assert result.exit_code == 0
    output = result.output.lower()
    for item in "generated", "open the file":
        assert item in output


def test_can_provide_custom_commands(runner, tmpdir):
    boca_dot_py = tmpdir.join("boca.py")

    boca_dot_py.write(
        cleandoc(
            """
    import click

    @click.group()
    def cli():
        pass

    @cli.command()
    def hello():
        click.echo("Hello!")
    """
        )
    )

    with env("BOCA_CUSTOM_COMMANDS_FILE", str(boca_dot_py)):
        cli = create_cli()

    result = runner.invoke(cli, ["hello"])

    assert result.exit_code == 0
    assert result.output == "Hello!\n"


def test_at_least_one_group_is_expected(runner, tmpdir):
    boca_dot_py = tmpdir.join("boca.py")
    boca_dot_py.write("import click")

    with env("BOCA_CUSTOM_COMMANDS_FILE", str(boca_dot_py)):
        with pytest.raises(ValueError):
            create_cli()
