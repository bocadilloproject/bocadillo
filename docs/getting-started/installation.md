# Installation

This page will get you up and running with Bocadillo.

## Install Python

Bocadillo being a Python web framework, it requires you to have Python installed.

You can download the latest Python version on [python.org](https://www.python.org/downloads/) or with your OS's package manager.

::: warning COMPATIBILITY NOTE
Bocadillo is compatible with **Python 3.6 and above**.
:::

::: tip NOTE
In the rest of the documentation, we will use `python` to refer to your Python executable. You may need to use `python3` depending on your operating system.
:::

To verify that Python is correctly installed, type `python` in your shell. You should see something like:

```
Python 3.7.2 (default, Dec 27 2018, 17:33:56)
[Clang 10.0.0 (clang-1000.11.45.5)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

## Install Bocadillo

Bocadillo is released to PyPI, so you can install using [pip](https://pip.pypa.io/en/stable/):

```bash
pip install bocadillo
```

## Verifying your installation

To verify that Bocadillo can be seen by Python, type `python` from your shell, then try to import it:

```python
>>> import bocadillo
>>> bocadillo.__version__
"0.13.3"
```

Alternatively, you can use an inline script:

```bash
python -c "import bocadillo; print(bocadillo.__version__)"
0.13.3
```

Note that you may have another version of Bocadillo installed.

## Extras <Badge text="Advanced" type="warning"/>

Beyond the base install, Bocadillo has pip extras for the following optional features:

| Feature                 | Extra      |
| ----------------------- | ---------- |
| [File responses]        | `files`    |
| [Cookie-based sessions] | `sessions` |

[file responses]: /guides/http/responses.md#file-responses
[cookie-based sessions]: /guides/http/sessions.md

Example `pip` invocations:

```bash
pip install bocadillo[files]
pip install bocadillo[files,sessions]
```

::: tip
To install all optional features, use `$ pip install bocadillo[full]`.
:::
