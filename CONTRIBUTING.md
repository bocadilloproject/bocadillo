# Contributing to Bocadillo

## Contents

- [Introduction](#introduction)
- [Getting started](#getting-started)
- [Code style](#code-style)
- [Pull Request process](#pull-request-process)
- [Notes to maintainers](#notes-to-maintainers)

## Introduction

### What is this document about?

Have you found a bug? You'd like to add a new feature or improve the docs? Fantastic news! All contributions are happily welcome.

Here, we point at a few guidelines that you should follow in order to get your contribution accepted.

### Always discuss ideas!

Before submitting any code changes for review, you should first **open an issue** so that maintainers and contributors can discuss it with you.

This step is important because there may be aspects you didn't think about, or there may be ways to expand or focus your suggestions. Eventually, discussing your suggestions with others can only improve the quality of the contribution you'll make.

## Getting started

Bocadillo has a single repository for both the `bocadillo` package and its documentation.

### Setting up the repo

Here's how to get your copy of the repo ready for development:

- Fork the `bocadilloproject/bocadillo` repo.
- Clone the repo on your computer: `git clone https://github.com/<your-username>/bocadillo.git`.
- Checkout the `master` branch and grab its latest version: `git pull origin master`.
- Install the project (see installation steps below).
- Create a branch (e.g. `fix/some-bug`) and work on it.
- Push to your remote: `git push origin fix/some-bug`.
- [Open a pull request] and follow the [PR process](#pull-request-process) below.

### Installing Bocadillo for development

#### Installing the `bocadillo` package

In order to install Bocadillo for development, you'll need **Python 3.6+**.

Project dependencies are managed through [Pipenv]. You should install it if you haven't already:

```bash
pip install pipenv
```

Then run the following in order to install dependencies:

```bash
pipenv install --dev
```

To verify Python dependencies have been correctly installed, first [run the tests](#running-tests). You can also fiddle with Bocadillo in the interpreter:

```python
>>> import bocadillo
>>> bocadillo.__version__
'0.12.0'
```

### Installing pre-commit hooks

This repo has a pre-commit hooks that runs Black (see [Black formatting](#black-formatting)) against your code before every commit.

After installing dependencies, you should install the hooks using the following command:

```shell
pre-commit install
```

#### Installing the documentation packages

If you're planning to contribute documentation, you should also install the npm dependencies. Make sure you have [Node] and [npm] installed, then run:

```bash
npm install
```

To verify the npm packages are correctly installed, you can fire up the docs site:

```bash
npm start
```

and access it at http://localhost:8080.

#### Running tests

Before making any changes, you should first run the tests in order to make sure everything is correcly setup.

Bocadillo uses [pytest] as its testing framework. The test suite can be run using:

```bash
pytest
```

To also generate a [coverage] report, run:

```bash
pytest --cov=./
```

### Contributing documentation

There are a few extra things you need to known in order to contribute documentation for Bocadillo.

This section supposes that you have already installed Bocadillo's [documentation dependencies](#installing-the-documentation-packages).

**Note**: Bocadillo's documentation site is made with [VuePress]. You may need to refer to its documentation, although the main problems you'll encounter are listed here.

#### How the documentation is structured

All documentation lives in the `docs/` directory. It is structured as follows:

- `getting-started`: resources for users getting started with Bocadillo.
- `guides`: discussions about key topics and concepts, including background, information and usage hints.
- `how-to`: recipes for solving key problems or addressing specific use cases.
- `discussions`: these give more in-depth background about important topics or activities related to application development.
- `api`: technical reference for Bocadillo's machinery, a majority of which is generated from the docstrings of Python modules, classes and functions.
- `faq`: frequently asked questions.

#### Running the docs site

To run the documentation site, run:

```bash
npm start
```

It will be accessible at http://localhost:8080.

The docs site is hot-reloaded on any changes to the contents of the `docs/` directory.

The only exception to this is the generated API Reference. You'll need to generate it to visualise it locally — see [Generating the API Reference](#generating-the-api-reference).

#### Creating documentation pages

To write a new page for the docs, create a new `.md` file in the appropriate directory (see [How the documentation is structured](#how-the-documentation-is-structured)), then add a route in the appropriate `sidebar` configuration in `docs/.vuepress/config.js`.

Feel free to refer to the [VuePress] docs if needed.

#### Generating the API Reference

Bocadillo uses [Pydoc-Markdown] to generate the API reference in Markdown format from Python docstrings. The generated `.md` files are then wired up in the `config.js` file.

In order to view the changes you've made to Python dosctrings in the docs site, or after your first install, you'll need to regenerate the API reference:

```bash
pymdoc generate
```

The docs site will reload and display the updated API Reference docs.

See [`pydocmd.yml`](./pydocmd.yml) for the configuration details and the [Pydoc-Markdown] documentation for usage reference.

#### Debugging the docs site

It may happen that the documentation site does not seem to behave properly.

You should first open your browser's dev tools and check for any errors. VuePress errors generally give enough clues as to what's wrong and how you can fix it.

If there is an issue with VuePress' hot-reloading, you may need to close the current tab and open a fresh copy of the docs site in a new tab.

## Code style

### Black formatting

In order to reduce format-related issues and make code reviews more efficient, this repo uses the [Black](https://github.com/ambv/black) formatter to format your code on commit. This is implemented using a [pre-commit](https://pre-commit.com) hook.

In practice, Black may intervene and reformat some of the Python files when committing to your local. When this happens, the commit will abort and you'll need to `git add` files edited by Black and `git commit` again.

If you wish to manually apply Black before a commit, run `$ pre-commit`.

Lastly, you can configure your IDE of choice to automatically format the code using Black (.e.g on save).

### Type annotations

Bocadillo makes heavy use of type annotations in order to document input and output types of functions and methods, as well as facilitate early detection of bugs.

You are encouraged to provide annotations for each and every function and method you write.

Do:

```python
def add(x: int, y: int) -> int:
    return x + y
```

Don't:

```
def add(x, y):
    return x + y
```

For background on the benefits of type annotations, we recommend Stav Shamir's [The other (great) benefit of Python type annotations](https://medium.com/@shamir.stav_83310/the-other-great-benefit-of-python-type-annotations-896c7d077c6b).

If you need help when writing type annotations, be sure to check out the official documentation of the [typing] module.

### Code documentation

Comments and docstrings are crucial in order to convey key information about the code. You should use them when needed.

Be sure, however, not to over-comment. **Code should be self-documenting**. For example, if you find yourself adding comments to delimit your code, it may be worth refactoring — e.g. into a few descriptively-named functions.

There are 3 types of code documentation you may find yourself using.

#### Module docstrings

All modules should have a descriptive docstring at their top. For example:

```python
"""Exception classes."""

class MyException(Exception):
    pass
```

#### Function, method or class docstrings

Every public function, method or class should have a proper docstring.

The formatting of the docstring is inspired by the [NumPyDoc] style. It should be followed so that your code can be properly picked up by [Pydoc-Markdown] to generate API reference.

Here is an example of a compliant class with its methods:

```python
"""Definition of the Foo class."""
import operator
from functools import reduce


class Foo:
    """Some really cool kind of foo.

    # Parameters
    bar (str): used to configure XYZ.
    """

    def __init__(self, bar: str):
        self._bar = bar

    @property
    def zed(self) -> str:
        """z with an exclamation mark."""
        return 'z!'

    def create_baz(self) -> int:
        """Create `baz` from the current `bar`.

        # Returns
        baz (int): multiplication the ASCII codes for each letter in `bar`.
        """
        return reduce(operator.mul, map(ord, self._bar))
```

#### Comments

A comment is a line that starts with `#`. There are two use cases to comments:

- To explain complex code that may not be easily understood by future developers.
- To explain **why** a portion of code was implemented the way it was.

As a rule of thumb, don't use comments to explain _what_ your code is doing, but to explain _why_ it's doing what it's doing. Again, code should be self-documenting. If you need to explain _what_ your code is doing, try simplifying it into smaller components (functions, methods, objects) with descriptive names.

## Linting

Linting refers to the process of running a program that will analyze the code base for potential errors. This repo uses two linters: Pylint and Mypy.

### PyLint

Pylint is used for general error checking. It has a lot of useful features which you can read about on the official website: [pylint.org](https://www.pylint.org).

Pylint comes installed along with the development dependencies, and can be used to check for errors using:

```
pylint bocadillo
```

FYI, the Pylint configuration is located in `pylintrc`.

### Static type checking with MyPy

MyPy is installed along with the development dependencies, so you can manually type check the code base using:

```bash
mypy bocadillo
```

We also encourage you to configure your IDE of choice to automatically type check the code using MyPy for you (e.g. on save).

## Pull Request process

1. Make sure to **open an issue** before submitting a PR (see [Always discuss ideas](#always-discuss-ideas)). Note: not all features can be accepted, as some may be out-of-scope and would be better off as third-party packages. It would be sad if you worked on a PR for days but it gets rejected because of reasons that could have been quickly pointed at if you discussed it in an issue.
2. Ensure your changes are well-commented and you haven't left any commented-out lines of code or debug `print` statements.
3. If your changes imply additions or changes in interface, make sure to the documentation. This includes environment variables, file locations, extra keyword arguments, etc.
4. You must add [tests](#running-tests) for the feature or bug fix you are providing.
5. Your PR must pass the Travis CI builds. It will not be merged if the tests fail.
6. The PR can be merged once it has obtained approval from at least one collaborator or maintainer.

## Notes to maintainers

**This section is solely aimed at maintainers and owners of the Bocadillo repository.**

### Versioning

Versioning is managed through [bumpversion](https://pypi.org/project/bumpversion/).

The utility script `scripts/bumpversion.sh` runs `bumpversion` with all the provided arguments\*, bumps the changelog and creates a tagged commit for the new version.

Example usage:

```bash
bash scripts/bumpversion.sh "patch | minor | major"
```

> Tip: you may want to `chmod +x scripts/bumpversion.sh` to use `./scripts/bumpversion.sh` for convenience.

\*See [bumpversion official docs](https://pypi.org/project/bumpversion/) for all the available options and `.bumpversion.cfg` for the default configuration.

### Releasing

This section documents how to release new versions to PyPI.

#### Testing

It is recommended to make a test release to TestPyPI before releasing a new version to production.

You can do so by pushing to the `release/test` branch.

- Grab the latest version from `master`:

```bash
git checkout release/test
git merge master
```

- If the current version has already been released to TestPyPI, update the package version (see [versioning](#versioning)).

- Push to remote:

```bash
git push
```

#### Production

When ready to release a new version to production:

- Update the package version if necessary (see [versioning](#versioning)).

- Push the tagged commit to remote:

```bash
$ git push --tags
```

[open a pull request]: https://github.com/bocadilloproject/bocadillo/compare
[type annotations]: https://medium.com/@shamir.stav_83310/the-other-great-benefit-of-python-type-annotations-896c7d077c6b
[typing]: https://docs.python.org/3/library/typing.html
[numpydoc]: https://numpydoc.readthedocs.io
[pydoc-markdown]: https://niklasrosenstein.github.io/pydoc-markdown/
[node]: https://nodejs.org/en
[npm]: https://www.npmjs.com
[pipenv]: https://github.com/pypa/pipenv
[pytest]: https://docs.pytest.org
[vuepress]: https://vuepress.vuejs.org
[coverage]: https://coverage.readthedocs.io
