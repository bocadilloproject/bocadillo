# Contributing to Bocadillo

All contributions to Bocadillo are welcome! Here are some guidelines to get you started.

## Documentation

Bocadillo's documentation site is made with [VuePress](https://vuepress.vuejs.org) and hosted on GitHub Pages.

To get started, you should only need to install NPM dependencies (`npm install`) and run `npm start` to run the hot-reloaded development docs site.

All documentation lives in the `docs/guide/` directory. It is structured as follows:

- `api-guides`: technical reference for Bocadillo's machinery; describes how it works and how to use it, assuming a basic understanding of the key concepts.
- `topics`: discuss key topics and concepts at a fairly high level, while providing useful information and background. For example: 'Working with JSON data'.
- `how-to`: recipes for solving common problems. For example: 'Deploying Bocadillo apps' or 'Writing custom CLI commands'.

To write a new page for the docs, create a new `.md` file in the appropriate directory, then update the `sidebar` configuration in `config.js` to add a route for your page in the sidebar.

Feel free to refer to the [VuePress docs](https://vuepress.vuejs.org) if needed.

### API Reference

Once you have installed Bocadillo for development (see next section) API Reference can be generate by using:

```bash
pymdoc generate
```

See `pymdoc.yml` and [PydocMarkdown] documentation for the details.

## Install

Python 3.6+ is required to install Bocadillo locally.

Install [Pipenv](https://github.com/pypa/pipenv) if you haven't already:

```bash
pip install pipenv
```

Then run:

```bash
pipenv install --dev
```

## Code style

To reduce format-related issues and make code review more efficient, this repo uses the [Black](https://github.com/ambv/black) auto-formatter to format your code on commit. This is implemented using [pre-commit](https://pre-commit.com).

If you wish to manually apply Black before a commit, run `$ pre-commit`.

## Running the tests

To run the test suite, run:

```bash
pytest
```

## Versioning

Versioning is managed through [bumpversion](https://pypi.org/project/bumpversion/).

To update the package's version, use:

```bash
bumpversion "patch | minor | major | post_release"
```

This will create a new commit tagged with the new version.

See [bumpversion official docs](https://pypi.org/project/bumpversion/) for all the available options.

## Releasing

This section documents how to release new versions to PyPI.

### Testing

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

### Production

When ready to release a new version to production:

- Update the package version if necessary (see [versioning](#versioning)).

- Push the tagged commit to remote:

```bash
$ git push --tags
```

[PydocMarkdown]: https://github.com/NiklasRosenstein/pydoc-markdown
