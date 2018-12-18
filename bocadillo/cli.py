"""Bocadillo CLI factory."""
import os
from inspect import getsource

import click

from . import __version__

CUSTOM_COMMANDS_FILE_ENV_VAR = "BOCA_CUSTOM_COMMANDS_FILE"


def get_custom_commands_path() -> str:
    return os.getenv(CUSTOM_COMMANDS_FILE_ENV_VAR, "boca.py")


def get_custom_commands_script_contents() -> str:
    from .scaffold import boca

    return getsource(boca)


class BocaCLI(click.Group):
    """Multi-command CLI that loads a group of commands from a file.

    Notes
    -----
    - Commands are loaded from a file determined by `path`, relative to the
    current working directory (i.e., when the CLI script is executed).
    - The first click.Group object found in that file is used as a source of
    commands.

    Inspired By
    -----------
    https://click.palletsprojects.com/en/7.x/commands/#custom-multi-commands
    """

    def __init__(self, path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._load_group(path)

    def _load_group(self, path: str):
        ns = {}

        try:
            with open(path, "r") as f:
                code = compile(source=f.read(), filename=path, mode="exec")
        except FileNotFoundError:
            # User did not create custom commands
            return
        else:
            eval(code, ns, ns)

        groups = (val for val in ns.values() if isinstance(val, click.Group))
        group = next(groups, None)
        if group is None:
            raise ValueError(
                f"Expected at least one group in {path}, none found."
            )
        for name, cmd in group.commands.items():
            self.add_command(cmd, name)


def create_cli() -> click.Command:
    """Create a Bocadillo CLI instance."""

    version_kwargs = {
        "prog_name": "Bocadillo",
        "message": "%(prog)s v%(version)s",
    }
    version_flags = ("-v", "-V", "--version")

    @click.group(cls=BocaCLI, path=get_custom_commands_path())
    @click.version_option(__version__, *version_flags, **version_kwargs)
    def cli():
        pass

    @cli.command()
    def version():
        """Show the version and exit."""
        click.echo(
            version_kwargs["message"]
            % {"prog": version_kwargs["prog_name"], "version": __version__}
        )

    @cli.command(name="init:custom")
    @click.option(
        "-d", "--directory", default="", help="Where files should be generated."
    )
    def init_custom(directory: str):
        """Generate files required to build custom commands."""
        contents = get_custom_commands_script_contents()
        path = os.path.join(directory, get_custom_commands_path())
        with open(path, "w") as f:
            f.write(contents)
        click.echo(click.style(f"Generated {path}", fg="green"))
        click.echo("Open the file and start building!")

    return cli
