<p align="center">
    <img src="https://github.com/bocadilloproject/bocadillo/blob/master/.github/banner.png?raw=true">
</p>

---

[![python](https://img.shields.io/pypi/pyversions/bocadillo.svg?logo=python&logoColor=fed749&colorB=3770a0&label=)](https://www.python.org)
[![pypi](https://img.shields.io/pypi/v/bocadillo.svg)][pypi-url]
[![travis](https://img.shields.io/travis/bocadilloproject/bocadillo.svg)](https://travis-ci.org/bocadilloproject/bocadillo)
[![black](https://img.shields.io/badge/code_style-black-000000.svg)](https://github.com/ambv/black)
[![codecov](https://codecov.io/gh/bocadilloproject/bocadillo/branch/master/graph/badge.svg)](https://codecov.io/gh/bocadilloproject/bocadillo)
[![license](https://img.shields.io/pypi/l/bocadillo.svg)][pypi-url]
[![Join the chat at https://gitter.im/bocadilloproject/bocadillo](https://badges.gitter.im/bocadilloproject/bocadillo.svg)](https://gitter.im/bocadilloproject/bocadillo)

[pypi-url]: https://pypi.org/project/bocadillo/

[Documentation][docs] / [CLI](https://github.com/bocadilloproject/queso) / [Twitter](https://twitter.com/bocadillopy) / [Blog](https://bocadilloproject.github.io/blog/) / [Mentions](https://bocadilloproject.github.io/mentions.html) / [FAQ](https://bocadilloproject.github.io/faq/)

[docs]: https://bocadilloproject.github.io

Bocadillo is a modern Python web framework that aims at making async web apps and services fun to build and accessible to everyone.

It is designed to be:

- **Productive**: a carefully chosen set of included batteries\* helps you solve common and more advanced problems.

- **Real-time capable**: embrace async programming and the baked-in WebSocket and SSE support to build real-time, highly-concurrent systems.

- **Flexible**: inject resources into web views using providers, an explicit, modular and easy-to-use mechanism inspired by pytest fixtures.

- **Performant**: Bocadillo is built on top of [Starlette] and [uvicorn], the lightning-fast ASGI toolkit and framework.

- **Empowering**: ships with testing and command line tools that help you build delicious, high-quality applications.

- **Transparent**: we make sure every single feature is documented front to back, and provide optimal editor support with a 100% type-annotated code base.

_\*The bucket list: HTTP, WebSocket, SSE, CORS, HSTS, GZip, Jinja2 templates, background tasks, streaming, middleware, redirection, error handling, class-based views, view hooks, media responses, file responses, attachments, static files serving, event handlers…_

[starlette]: https://www.starlette.io
[uvicorn]: https://www.starlette.io

## Quick start

We all love delicious "Hello, world!" examples, don't we? Here's ours:

1. Install Bocadillo:

```bash
pip install bocadillo
```

2. Write the app:

```python
from bocadillo import App

app = app()

@app.route("/")
async def index(req, res):
    res.text = "Hello, world!"

if __name__ == "__main__":
    app.run()
```

3. Start the server:

```bash
python app.py
```

4. Say hello!

```bash
$ curl http://localhost:8000
Hello, world!
```

Tastes good! 🥪

Hungry for more? Head to the [docs].

## Changelog

Changes made to Bocadillo across releases are recorded in the [Changelog](https://github.com/bocadilloproject/bocadillo/blob/master/CHANGELOG.md). Be sure to check it out to see where we're coming from!

## Roadmap

For a list of short, mid and long-term feature ideas currently in our scope, see the [Roadmap](https://github.com/bocadilloproject/bocadillo/blob/master/ROADMAP.md).

To see what has already been implemented for the next release, see the [Unreleased section of the changelog](https://github.com/bocadilloproject/bocadillo/blob/master/CHANGELOG.md#unreleased).

## Contributing

Found a bug? A typo? Want to help build a new feature? We'd love to see your contributions! There are also many ways to contribute that don't include code: helping with issues, laying out new ideas, improving docs, etc.

Check out our [Contributing guide](https://github.com/bocadilloproject/bocadillo/blob/master/CONTRIBUTING.md) for more information.

By the way, here's our Contributor Hall of Fame:

[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/0)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/0)[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/1)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/1)[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/2)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/2)[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/3)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/3)[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/4)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/4)[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/5)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/5)[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/6)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/6)[![](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/images/7)](https://sourcerer.io/fame/florimondmanca/bocadilloproject/bocadillo/links/7)

## Credits

Logo designed by Florimond Manca. Sandwich icon designed by [macrovector](http://macrovector.com).
