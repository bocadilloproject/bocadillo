# Bocadillo

[![license](https://img.shields.io/pypi/l/bocadillo.svg)][pypi-url]
[![pypi](https://img.shields.io/pypi/v/bocadillo.svg)][pypi-url]
[![travis](https://img.shields.io/travis-ci/florimondmanca/bocadillo.svg)][travis-url]  
[![python](https://img.shields.io/pypi/pyversions/bocadillo.svg)][pypi-url]

Inspired by [Responder](http://python-responder.org), Bocadillo is a web framework that combines ideas from Falcon and Flask while leveraging modern Python async capabilities.

Under the hood, it uses the [Starlette](https://www.starlette.io) ASGI toolkit and the [uvicorn](https://www.uvicorn.org) ASGI server.

## Quick start

Write your first app:

```python
# app.py
import bocadillo

api = bocadillo.API()

@api.route('/add/{x:d}/{y:d}')
async def greet(req, resp, x: int, y: int):
    resp.media = {'result': x + y}

if __name__ == '__main__':
    api.run()
```

Run it:

```bash
python app.py
# or directly using uvicorn:
uvicorn app:api
```

```
INFO: Started server process [81910]
INFO: Waiting for application startup.
INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Make some requests!

```bash
curl http://localhost:8000/add/3/5
{"result": 5}
```

🌯💥

## Install

Bocadillo is available on PyPI:

```bash
pip install bocadillo
```

## Features

- ASGI-compatible app
- Flask-inspired decorator-based routing
- Formatted string route patterns
- Falcon-inspired passing of request and response
- Send JSON responses using `resp.media`
- Class-based views
- Response headers
- Status codes
- HTTP error exceptions
- Jinja2 template rendering
- Static assets
- Mount any WSGI or ASGI app as sub-apps.

TODO:

- Bocadillo CLI
- Deployment guide

## Contributing

See [CONTRIBUTING](CONTRIBUTING.md) for contribution guidelines.

## Changelog

See [CHANGELOG](CHANGELOG.md) for a chronological log of changes to Bocadillo.

<!-- URLs -->

[travis-url]: https://travis-ci.org/florimondmanca/bocadillo

[pypi-url]: https://pypi.org/project/bocadillo/
