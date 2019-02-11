<p align="center">
    <img src="https://github.com/bocadilloproject/bocadillo/blob/master/.github/banner.png?raw=true">
</p>

---

[![python](https://img.shields.io/pypi/pyversions/bocadillo.svg?logo=python&logoColor=fed749&colorB=3770a0&label=)][python-url]
[![pypi](https://img.shields.io/pypi/v/bocadillo.svg)][pypi-url]
[![downloads](https://pepy.tech/badge/bocadillo)][pepy-url]
[![travis](https://img.shields.io/travis/bocadilloproject/bocadillo.svg)][travis-url]
[![black](https://img.shields.io/badge/code_style-black-000000.svg)][black]
[![codecov](https://codecov.io/gh/bocadilloproject/bocadillo/branch/master/graph/badge.svg)][codecov]
[![license](https://img.shields.io/pypi/l/bocadillo.svg)][pypi-url]
[![Join the chat at https://gitter.im/bocadilloproject/bocadillo](https://badges.gitter.im/bocadilloproject/bocadillo.svg)][gitter-url]

# Bocadillo

Bocadillo is a Python web framework that provides a sane toolkit for quickly building performant web applications and services, while encouraging best practices and keeping developer experience in mind.

Under the hood, it uses the [Starlette](https://www.starlette.io) ASGI toolkit and the lightning-fast [uvicorn](https://www.uvicorn.org) ASGI server.

[Read the documentation][docs]

## Quick start

Install it:

```bash
pip install bocadillo
```

Build something:

```python
# api.py
import bocadillo

api = bocadillo.API()

@api.route("/")
async def index(req, res):
    # Use a template from the ./templates directory 
    res.html = await api.template("index.html")

@api.route("/greet/{person}")
async def greet(req, res, person):
    res.media = {"message": f"Hi, {person}!"}

if __name__ == "__main__":
    api.run()
```

Launch:

```bash
python api.py
```

Make requests!

```bash
curl http://localhost:8000/greet/Bocadillo
{"message": "Hi, Bocadillo!"}
```

Hungry for more? Head to the [docs].

## Contributing

See [CONTRIBUTING](https://github.com/bocadilloproject/bocadillo/blob/master/CONTRIBUTING.md) for contribution guidelines.

## Changelog

See [CHANGELOG](https://github.com/bocadilloproject/bocadillo/blob/master/CHANGELOG.md) for a chronological log of changes to Bocadillo.

## Roadmap

For a list of short, mid and long-term feature ideas currently in our scope, see the [Roadmap][roadmap].

To see what has already been implemented for the next release, see the [Unreleased][changelog-unreleased] section of our changelog.

## Credits

Logo:

- Designed by Florimond Manca.
- Sandwich icon designed by [macrovector](http://macrovector.com).

<!-- URLs -->

[python-url]: https://www.python.org
[travis-url]: https://travis-ci.org/bocadilloproject/bocadillo
[pepy-url]: https://pepy.tech/project/bocadillo
[pypi-url]: https://pypi.org/project/bocadillo/
[Orator]: https://orator-orm.com
[docs]: https://bocadilloproject.github.io
[black]: https://github.com/ambv/black
[codecov]: https://codecov.io/gh/bocadilloproject/bocadillo
[gitter-url]: https://gitter.im/bocadilloproject/bocadillo
[roadmap]: https://github.com/bocadilloproject/bocadillo/blob/master/ROADMAP.md
[changelog-unreleased]: https://github.com/bocadilloproject/bocadillo/blob/master/CHANGELOG.md#unreleased
