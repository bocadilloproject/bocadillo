# Contributing to Bocadillo

All contributions to Bocadillo are welcome! Here are some guidelines to get you started.

## Install

Python 3.6+ is required.

Install [Pipenv](https://github.com/pypa/pipenv) if you haven't already:

```bash
pip install pipenv
```

Then run:

```bash
pipenv install
```

## Running the tests

To run the test suite, run:

```bash
pytest
```

## Versioning

Versioning is managed through [bumpversion](https://pypi.org/project/bumpversion/).

To update the package's version, use:

```bash
bumpversion "patch | minor | major"
```

This will create a new commit with the new version.

To create a new tag, use the `--tag` option.

See [bumpversion official docs](https://pypi.org/project/bumpversion/) for all the available options.

## Releasing

This section documents how to release new versions to PyPI.

### Testing

It is recommended to make a test release to TestPyPI before releasing a new version to production.

You can do so by pushing to the `release/test` branch.

- Gab the latest version from `master`:

```bash
git checkout release/test
git merge master
```

- If the current version has already been released to TestPyPI, update the package version (see [versioning](#versioning)).

- Push to remote:

```bash
git push
```

### Production

When ready to release a new version to production:

- Update the package version with `--tag` (see [versioning](#versioning)).

- Push the tagged commit to remote:

```bash
$ git push --tags
```
