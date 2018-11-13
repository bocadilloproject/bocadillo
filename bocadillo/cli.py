"""Bocadillo CLI factory."""
import os
from inspect import cleandoc
from typing import List

from .ext import click

CUSTOM_COMMANDS_FILE_ENV_VAR = 'BOCA_CUSTOM_COMMANDS_FILE'


def get_custom_commands_file_path():
    return os.getenv(CUSTOM_COMMANDS_FILE_ENV_VAR, 'boca.py')


class FileGroupCLI(click.MultiCommand):
    """Multi-command CLI that loads a group of commands from a file.

    Notes
    -----
    - Commands are loaded from a file determined by `file_name`, relative to the
    current working directory (i.e., when the CLI script is executed).
    - The first click.Group object found in that file is used as a source of
    commands.

    Inspired By
    -----------
    https://click.palletsprojects.com/en/7.x/commands/#custom-multi-commands
    """

    def __init__(self, file_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._group: click.Group = None
        self.file_name = file_name

    def _load_group(self):
        ns = {}
        path = self.file_name

        try:
            with open(path, 'r') as f:
                code = compile(source=f.read(), filename=path, mode='exec')
                eval(code, ns, ns)
        except FileNotFoundError:
            # User did not create custom commands, use an empty group.
            self._group = click.Group()
            return

        for key, value in ns.items():
            if isinstance(value, click.Group):
                self._group = value
                break
        else:
            raise click.ClickException(
                f'Expected at least one group in {path}, none found.'
            )

    @property
    def group(self) -> click.Group:
        """Lazy-loaded, cached group object."""
        if self._group is None:
            self._load_group()
        return self._group

    def list_commands(self, ctx: click.Context) -> List[str]:
        return self.group.list_commands(ctx)

    def get_command(self, ctx: click.Context, name: str) -> click.Command:
        return self.group.get_command(ctx, name)


def create_cli() -> click.Command:
    @click.group()
    def builtin():
        pass

    @builtin.command(name='help')
    @click.pass_context
    def help_(ctx):
        """Show help about boca."""
        click.echo(ctx.parent.get_help())

    @builtin.command(name='init:custom')
    @click.option('-d', '--directory', default='',
                  help='Where files should be generated.')
    def init_custom(directory: str):
        """Generate files required to build custom commands."""
        custom_commands_script_contents = cleandoc(
            '''"""Custom Bocadillo commands.
    
            Use Click to build custom commands. For documentation, see:
            https://click.palletsprojects.com
            """
            from bocadillo.ext import click
    
    
            @click.group()
            def cli():
                pass
    
            # Write your @cli.command() functions below.\n
            '''
        ) + '\n'
        path = os.path.join(directory, get_custom_commands_file_path())
        with open(path, 'w') as f:
            f.write(custom_commands_script_contents)
        click.echo(click.style(f'Generated {path}', fg='green'))
        click.echo('Open the file and start building!')

    custom = FileGroupCLI(
        file_name=get_custom_commands_file_path(),
    )

    # Builtins first to prevent override in custom commands.
    return click.CommandCollection(sources=[builtin, custom])


# Exposed to the setup.py entry point
cli = create_cli()
