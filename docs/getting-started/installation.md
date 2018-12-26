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
Python 3.7.0 (default, Jun 29 2018, 20:13:13) 
[Clang 9.1.0 (clang-902.0.39.2)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> 
```

## Install Bocadillo

### From PyPI

Bocadillo is released to PyPI, which means you can install using [pip](https://pip.pypa.io/en/stable/):

```bash
pip install bocadillo
```

### From source (advanced)

For enthusiasts and contributors, Bocadillo can also be installed from source.

You'll first need to clone the repository. Then, move to Bocadillo's root directory and run:

```bash
pip install .
```

Alternatively, use the `-e` option for an [editable installation](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs).

## Verifying your installation

To verify that Bocadillo can be seen by Python, type `python` from your shell, then try to import it:

```python
>>> import bocadillo
>>> bocadillo.__version__
'0.8.0'
```

Alternatively, you can use an inline script:
```bash
python -c "import bocadillo; print(bocadillo.__version__)"
0.8.0
```

Note that you may have another version of Bocadillo installed.

Now that you're all set up, go take a look at our [quickstart](./quickstart.md) guide to see some of Bocadillo's most delicious features.
