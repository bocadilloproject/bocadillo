<p align="center">
    <img src="https://github.com/bocadilloproject/bocadillo/blob/master/.github/banner.png?raw=true">
</p>

---

[![python](https://img.shields.io/pypi/pyversions/bocadillo.svg?logo=python&logoColor=fed749&colorB=3770a0&label=)](https://www.python.org)
[![pypi](https://img.shields.io/pypi/v/bocadillo.svg)][pypi-url]
[![downloads](https://pepy.tech/badge/bocadillo)](https://pepy.tech/project/bocadillo)
[![travis](https://img.shields.io/travis/bocadilloproject/bocadillo.svg)](https://travis-ci.org/bocadilloproject/bocadillo)
[![black](https://img.shields.io/badge/code_style-black-000000.svg)](https://github.com/ambv/black)
[![codecov](https://codecov.io/gh/bocadilloproject/bocadillo/branch/master/graph/badge.svg)](https://codecov.io/gh/bocadilloproject/bocadillo)
[![license](https://img.shields.io/pypi/l/bocadillo.svg)][pypi-url]
[![Join the chat at https://gitter.im/bocadilloproject/bocadillo](https://badges.gitter.im/bocadilloproject/bocadillo.svg)](https://gitter.im/bocadilloproject/bocadillo)

[pypi-url]: https://pypi.org/project/bocadillo/

# Bocadillo

Bocadillo is a Python web framework that provides a sane toolkit for quickly building performant web applications and services, while encouraging best practices and keeping developer experience in mind.

Under the hood, it uses the [Starlette](https://www.starlette.io) ASGI toolkit and the lightning-fast [uvicorn](https://www.uvicorn.org) ASGI server.

[Read the documentation][docs]

[docs]: https://bocadilloproject.github.io

## Quick start

Install it:

```bash
pip install bocadillo
```

Build something:

```python
# app.py
from bocadillo import App, Templates

app = App()
templates = Templates(app)

@app.route("/")
async def index(req, res):
    # Use a template from the ./templates directory
    res.html = await templates.render("index.html")

@app.route("/greet/{person}")
async def greet(req, res, person):
    res.media = {"message": f"Hi, {person}!"}

if __name__ == "__main__":
    app.run()
```

Launch:

```bash
python app.py
```

Make requests!

```bash
curl http://localhost:8000/greet/Bocadillo
{"message": "Hi, Bocadillo!"}
```

Hungry for more? Head to the [docs].

## Changelog

Changes made to Bocadillo across releases are recorded in the [Changelog](https://github.com/bocadilloproject/bocadillo/blob/master/CHANGELOG.md). Be sure to check it out to see where we're coming from!

## Roadmap

For a list of short, mid and long-term feature ideas currently in our scope, see the [Roadmap](https://github.com/bocadilloproject/bocadillo/blob/master/ROADMAP.md).

To see what has already been implemented for the next release, see the [Unreleased section of the changelog](https://github.com/bocadilloproject/bocadillo/blob/master/CHANGELOG.md#unreleased).

## Contributing

Found a bug? A typo? Want to build a new feature? We'd love to see your contributions! There are also many ways to contribute that don't include code: helping with issues, laying out new ideas, improving docs, etc.

Check out our [Contributing guide](https://github.com/bocadilloproject/bocadillo/blob/master/CONTRIBUTING.md) for more information.

By the way, here's our Contributor Hall of Fame:

[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/0)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/0)[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/1)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/1)[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/2)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/2)[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/3)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/3)[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/4)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/4)[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/5)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/5)[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/6)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/6)[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/7)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/7)

## Credits

Logo designed by Florimond Manca. Sandwich icon designed by [macrovector](http://macrovector.com).
