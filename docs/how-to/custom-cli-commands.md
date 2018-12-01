# Writing custom CLI commands

::: warning
This CLI extension mechanism is experimental and may be subject to changes.
:::

Bocadillo provides a handy [CLI](../topics/tooling/cli.md) for performing common tasks. If you find yourself repeating certain tasks, you can automate them via a custom `boca` command.

To do so, use the `init:custom` command, which will generate the following file:

```python
# boca.py
"""Custom Bocadillo commands.

Use Click to build custom commands. For documentation, see:
https://click.palletsprojects.com
"""
from bocadillo.ext import click


@click.group()
def cli():
    pass

# Write your @cli.command() functions below.

```

The `cli` group will be picked up and its commands merged into `boca`, provided you are located at the same level than the custom commands script.

For example, let's add a `boca hello` command:

```python
# boca.py
@cli.command()
def hello():
    """Show a friendly message."""
    click.echo('Hello from a custom command!')
```

Now see it in action:

```
$ ls
app.py  boca.py
$ boca hello --help
Usage: boca hello [OPTIONS]

  Show a friendly message.

Options:
  --help  Show this message and exit.

$ boca hello
Hi from a custom command!
```

> **Tip**: the name of the custom commands file can be customized by setting the `BOCA_CUSTOM_COMMANDS_FILE` environment variable.

Of course, you can leverage Click's awesome features when building custom commands. See the [Click docs](https://click.palletsprojects.com) for more information.
