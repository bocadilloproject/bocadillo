from bocadillo.ext import click


@click.group()
def cli():
    pass


@cli.command()
def hi():
    """Show a friendly hello message."""
    click.echo('Hi, there!')
