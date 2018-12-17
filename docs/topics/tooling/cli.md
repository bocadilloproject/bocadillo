# CLI

Bocadillo comes with `boca`, a handy CLI built with [Click] for performing common tasks when working on Bocadillo apps.

## Basic usage

```
Usage: boca [OPTIONS] COMMAND [ARGS]...

Options:
  -v, -V, --version  Show the version and exit.
  --help             Show this message and exit.

Commands:
  init:custom  Generate files required to build custom commands.
  version      Show the version and exit.
```

## Extending `boca`

You can write custom CLI commands to help you automate certain tasks.

See our how-to guide: [Write custom CLI commands].

[Click]: https://click.palletsprojects.com
[Write custom CLI commands]: ../../how-to/custom-cli-commands.md
