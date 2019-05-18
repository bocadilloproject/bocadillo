# Contributing to Bocadillo

Have you found a bug? You'd like to add a new feature or improve the docs? Fantastic news! All contributions are happily welcome.

Here, we point at a few guidelines that you should follow in order to get your contribution accepted.

**Note**: before submitting any code changes for review, you should first **open an issue** so that maintainers and contributors can discuss it with you.

This step is important because there may be aspects you didn't think about, or there may be ways to expand or focus your suggestions. Eventually, discussing your suggestions with others can only improve the quality of the contribution you'll make.

## Contents

- [Getting started](#getting-started)
- [Code style](#code-style)
- [Pull Request process](#pull-request-process)
- [Notes to maintainers](#notes-to-maintainers)

## Getting started

Bocadillo has a single repository for both the `bocadillo` package and its documentation.

**Note**: you will need **Python 3.6+** installed on your machine.

### Setting up the repo

1. Fork the `bocadilloproject/bocadillo` repo and clone it.

2. Install the dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pre-commit install
```

3. If you plan to contribute documentation, make sure you have [Node.js](https://nodejs.org/en) installed, and run:

```bash
npm install
```

### Retrieving upstream changes

1. Add this repo as an upstream: `git remote add upstream https://github.com/bocadilloproject/bocadillo.git`.
2. Check out the target branch, e.g. `git checkout master`.
3. Pull changes from the upstream remote repository: `git pull origin upstream`.

### Working with the repo

Testing and other tooling is automated through [`nox`](https://nox.thea.codes/en/stable/index.html):

- To run the [`pytest`](https://docs.pytest.org) test suite, run:

```bash
nox -s tests
```

- To also generate a coverage report, run:

```bash
nox -s tests -- coverage
```

- To also only show lines not covered by tests, run:

```
nox -s tests -- coverage missing
```

- To serve the docs site (built with [vuepress], hot reload enabled), run:

[vuepress]: https://vuepress.vuejs.org

```bash
nox -s docs -- serve
```

- To build the docs site, run:

```bash
nox -s docs
```

### Creating documentation pages

To add a new page to the docs, create a new `.md` file in the appropriate subdirectory of `docs` (`getting-started`, `guides`, `how-to` or `discussions`), then add a route in the appropriate `sidebar` configuration in `docs/.vuepress/config.js`.

Feel free to refer to the [VuePress] docs if needed.

### Generating the API Reference

The API reference is automatically generated with [Pydoc-Markdown] when running `nox -s docs` or `nox -s docs -- serve`.

[pydoc-markdown]: https://niklasrosenstein.github.io/pydoc-markdown/

If you need to regenerate it manually, run:

```bash
nox -s docs -- api
```

If it is running, the docs site should reload and display the updated API reference.

See [`pydocmd.yml`](./pydocmd.yml) for the configuration details and the [Pydoc-Markdown] documentation for usage reference.

## Code style

- **Formatting**: this repo has a pre-commit hook that runs [Black](https://github.com/ambv/black) against your code before each commit.

- **Type annotations**: we encourage you to provide type annotations (see [typing](https://docs.python.org/3/library/typing.html)) for functions, variables, methods and classes, e.g.:

```python
def add(x: int, y: int) -> int:
    return x + y
```

- **Comments**: code should be self-documenting. Only add comments to explain _why_ a piece of code was implemented the way it was, and couldn't be simplified further.

- **Linting**: this repo uses `pylint` for general-purpose linting and `mypy` for type checking. FYI, the Pylint configuration is located in [`pylintrc`](./pylintrc).

## Pull Request process

1. Make sure to **open an issue** before submitting a PR.
2. Ensure your changes are well-commented, and you haven't left any commented-out lines or `print()` statements.
3. Make sure to **update the documentation** if necessary.
4. Make sure you provided **new tests** for the feature or bug fix you are contributing.
5. Your PR must pass the Travis CI builds. It will not be merged if the tests fail.
6. Once the tests pass, your PR must be approved by a collaborator or maintainer before being merged in.
7. Your PR has been merged, congrats!

## Notes to maintainers

**This section is solely aimed at maintainers and owners of the Bocadillo repository.**

### Versioning

Versioning is managed through [bumpversion](https://pypi.org/project/bumpversion/).

To bump the package to a new version, use:

```bash
nox -s bumpversion -- "patch | minor | major"
```

This will update the version and the changelog, commit the changes and create a new tag.

\*See `.bumpversion.cfg` for configuration, and [bumpversion official docs](https://pypi.org/project/bumpversion/) for all the available options.

### Releasing

When ready to release a new version:

- Update the package version (see [versioning](#versioning)).
- Push the tagged commit to the remote repository:

```bash
$ git push --tags
```

A PyPI deploy will run at the end of the triggered Travis build.

### Hot fixes

The `stable` branch must be kept up to date with the latest release. When you need to release a bug fix as soon as possible, here's how to proceed:

1. Checkout out the `stable` branch.
2. Branch off from it to work on the hot fix.
3. When ready, push a PR to GitHub, using `stable` as the base. Make sure tests pass and everything looks fine.
4. Bump the version as a `patch (see [versioning](#versioning)) and follw [Releasing](#releasing).
