"""Custom Bocadillo commands.

Use Click to build custom commands. For documentation, see:
https://click.palletsprojects.com
"""
from bocadillo.ext import click


@click.group()
def cli():
    pass

# Write your @cli.command() functions below.
