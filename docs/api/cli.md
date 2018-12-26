# bocadillo.cli

## create_cli
```python
create_cli() -> click.core.Command
```
This is the Bocadillo CLI factory.

::: tip
Use this function to obtain an instance of `boca` for programmatic use.
:::

__Returns__

`cli (click.Command)`: an instance of the `boca` CLI.

## FileGroup
```python
FileGroup(self, path: str, *args, **kwargs)
```
A Click [MultiCommand] that loads a group of commands from a file.

::: warning
You should not need to interact with this class directly.
:::

[MultiCommand]: http://click.palletsprojects.com/en/7.x/api/#click.MultiCommand

__Parameters__

- __path (str)__:
    Path to a Python module declaring at least one Click group, from which
    extra commands will be obtained.


