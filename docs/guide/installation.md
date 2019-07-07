# Installation

## Basics

Bocadillo can be installed using the following command:

```bash
pip install bocadillo
```

**Note**:

- You will need **Python 3.6 and above** to use Bocadillo. You can get Python from [python.org](https://www.python.org/downloads/) or via the package manager of your OS.
- On Linux, due to [a known limitation in httptools](https://github.com/MagicStack/httptools/issues/33), you also need to install `python-dev` for your current version of Python, e.g. `apt-get install python3.7-dev` for Python 3.7.

## Bocadillo CLI

You may also want to install [Bocadillo CLI](https://github.com/bocadilloproject/bocadillo-cli). It comes with useful command line tools to help with project generation and other common tasks.

Install it from `pip`:

```bash
pip install bocadillo-cli
```

You can use it to verify that Bocadillo was correctly installed (you may have another version of Bocadillo installed):

```bash
$ bocadillo -V
Bocadillo CLI: 0.2.0
Bocadillo: 0.18.0
```

## Extras <Badge text="Advanced" type="warning"/>

Beyond the base install, Bocadillo has pip extras for the following optional features:

| Feature                 | Extra      |
| ----------------------- | ---------- |
| [File responses]        | `files`    |
| [Cookie-based sessions] | `sessions` |

[file responses]: /guide/responses.md#file-responses
[cookie-based sessions]: /guide/sessions.md

Example `pip` invocations:

```bash
pip install bocadillo[files]
pip install bocadillo[files,sessions]
```

::: tip
To install all optional features, use `$ pip install bocadillo[full]`.
:::
