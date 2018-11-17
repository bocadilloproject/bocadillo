<p align="center">
    <img src="https://github.com/florimondmanca/bocadillo/blob/master/assets/bocadillo.png">
</p>

<p align="center">
    <em>A modern Python web framework filled with asynchronous salsa.</em>
</p>

---

[![travis](https://img.shields.io/travis-ci/florimondmanca/bocadillo.svg)][travis-url]
[![python](https://img.shields.io/pypi/pyversions/bocadillo.svg)][pypi-url]
[![downloads](https://pepy.tech/badge/bocadillo)](https://pepy.tech/project/bocadillo)
[![pypi](https://img.shields.io/pypi/v/bocadillo.svg)][pypi-url]
[![license](https://img.shields.io/pypi/l/bocadillo.svg)][pypi-url]

# Bocadillo

Inspired by [Responder](http://python-responder.org), Bocadillo is a web framework that combines ideas from Falcon and Flask while leveraging modern Python async capabilities.

Under the hood, it uses the [Starlette](https://www.starlette.io) ASGI toolkit and the [uvicorn](https://www.uvicorn.org) ASGI server.

## Contents

- [Quick start](#quick-start)
- [Install](#install)
- [Usage](#Usage)
- [Contributing](#contributing)
- [Changelog](#changelog)
- [Roadmap](#roadmap)

## Quick start

Write your first app:

```python
# app.py
import bocadillo

api = bocadillo.API()

@api.route('/add/{x:d}/{y:d}')
async def add(req, resp, x: int, y: int):
    resp.media = {'result': x + y}

if __name__ == '__main__':
    api.run()
```

Run it:

```bash
python app.py
```

```
INFO: Started server process [81910]
INFO: Waiting for application startup.
INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Make some requests!

```bash
curl "http://localhost:8000/add/1/2"
{"result": 3}
```

🌯💥

Want more? Head to the [docs].

## Install

Bocadillo can be installed from source or from PyPI:

```bash
pip install bocadillo
```

## Usage

All usage documentation has been moved to the [docs] site.

## Contributing

See [CONTRIBUTING](https://github.com/florimondmanca/bocadillo/blob/master/CONTRIBUTING.md) for contribution guidelines.

## Changelog

See [CHANGELOG](https://github.com/florimondmanca/bocadillo/blob/master/CHANGELOG.md) for a chronological log of changes to Bocadillo.

## Roadmap

If you are interested in the future features that may be implemented into Bocadillo, take a look at our [milestones](https://github.com/florimondmanca/bocadillo/milestones?with_issues=no).

To see what has already been implemented for the next release, see the [Unreleased](https://github.com/florimondmanca/bocadillo/blob/master/CHANGELOG.md#unreleased) section of our changelog.

<!-- URLs -->

[travis-url]: https://travis-ci.org/florimondmanca/bocadillo
[pypi-url]: https://pypi.org/project/bocadillo/
[Orator]: https://orator-orm.com
[docs]: https://florimondmanca.github.io/bocadillo
