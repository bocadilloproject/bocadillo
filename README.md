<p align="center">
    <img src="https://github.com/bocadilloproject/bocadillo/blob/master/.github/banner.png?raw=true">
</p>

<p align="center">
    <a href="https://travis-ci.org/bocadilloproject/bocadillo">
        <img src="https://travis-ci.org/bocadilloproject/bocadillo.svg?branch=master" alt="Build status"/>
    </a>
    <a href="https://codecov.io/gh/bocadilloproject/bocadillo">
        <img src="https://codecov.io/gh/bocadilloproject/bocadillo/branch/master/graph/badge.svg" alt="Test coverage"/>
    </a>
    <a href="https://pypi.org/project/bocadillo">
        <img src="https://badge.fury.io/py/bocadillo.svg" alt="pypi version">
    </a>
    <a href="https://github.com/ambv/black">
        <img src="https://img.shields.io/badge/code_style-black-000000.svg" alt="code style">
    </a>
</p>

<p align="center">
    <a href="https://github.com/timofurrer/awesome-asyncio">
        <img src="https://awesome.re/mentioned-badge-flat.svg" alt="Mentioned in awesome-asyncio">
    </a>
    <a href="https://twitter.com/bocadillopy">
        <img src="https://img.shields.io/twitter/follow/bocadillopy.svg?label=%40bocadillopy&style=social" alt="@bocadillopy on Twitter">
    </a>
</p>

---

Documentation: [https://bocadilloproject.github.io][docs]

[docs]: https://bocadilloproject.github.io

---

Bocadillo is a **Python async web framework** that makes building performant and highly concurrent web APIs fun and accessible to everyone.

## Requirements

Python 3.6+

## Installation

```bash
pip install bocadillo
```

## Example

```python
from bocadillo import App, configure

app = App()
configure(app)

@app.route("/")
async def index(req, res):
    res.json = {"hello": "world"}
```

Save this as `app.py`, then start a [uvicorn](https://www.uvicorn.org) server (hot reload enabled!):

```bash
uvicorn app:app --reload
```

Say hello!

```bash
$ curl http://localhost:8000
{"hello": "world"}
```

Ready to dive in? [Visit the documentation site][docs].

## Changelog

All changes to Bocadillo are recorded in the [changelog](https://github.com/bocadilloproject/bocadillo/blob/master/CHANGELOG.md). To see what's coming in the next release, read the [Unreleased](https://github.com/bocadilloproject/bocadillo/blob/master/CHANGELOG.md#unreleased) section.

Release notes may also be published as blog posts on [Bocadillo News](https://bocadilloproject.github.io/news/).

## Contributing

Found a bug? A typo? Want to help build a new feature? We'd love to see your contributions! There are also many ways to contribute that don't include code: helping with issues, laying out new ideas, improving docs, etc.

Check out the [Contributing guide](https://github.com/bocadilloproject/bocadillo/blob/master/CONTRIBUTING.md) to get started.

By the way, here is the Bocadillo Contributor Hall of Fame. 👨‍💻👩‍💻

[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/0)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/0)[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/1)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/1)[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/2)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/2)[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/3)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/3)[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/4)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/4)[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/5)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/5)[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/6)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/6)[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/7)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/7)

## Credits

Logo designed by Florimond Manca. Sandwich icon designed by [macrovector](http://macrovector.com).
