from bocadillo.ext import click


@click.group()
def cli():
    pass


# Example command:
@cli.command()
def hello():
    """Prints a friendly message."""
    click.echo('Hi from a custom command!')
