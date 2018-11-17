<p align="center">
    <img src="https://github.com/bocadilloproject/bocadillo/blob/master/docs/.vuepress/public/banner.png">
</p>

<p align="center">
    <em>A modern Python web framework filled with asynchronous salsa.</em>
</p>

---

[![travis](https://img.shields.io/travis-ci/bocadilloproject/bocadillo.svg)][travis-url]
[![python](https://img.shields.io/pypi/pyversions/bocadillo.svg)][pypi-url]
[![downloads](https://pepy.tech/badge/bocadillo)][pepy-url]
[![pypi](https://img.shields.io/pypi/v/bocadillo.svg)][pypi-url]
[![license](https://img.shields.io/pypi/l/bocadillo.svg)][pypi-url]

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

@api.route('/')
async def index(req, res):
    res.html = await api.template('index.html')

@api.route('/greet/{person}')
def greet(req, res, person):
    res.media = {'message': f'Hi, {person}!'}

if __name__ == '__main__':
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

To see what has already been implemented for the next release, see the [Unreleased](https://github.com/bocadilloproject/bocadillo/blob/master/CHANGELOG.md#unreleased) section of our changelog.

<!-- URLs -->

[travis-url]: https://travis-ci.org/bocadillo/bocadillo
[pepy-url]: https://pepy.tech/project/bocadillo
[pypi-url]: https://pypi.org/project/bocadillo/
[Orator]: https://orator-orm.com
[docs]: https://bocadilloproject.github.io
