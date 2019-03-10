# Testing

This page documents ways in which Bocadillo can help you write great tests and ensure the quality of your apps, as well as hints for integrating with your favorite test framework.

## Helpers

### Test client

The [`create_client`](/api/testing.md#create-client) helper can be used to build a [Starlette `TestClient`](https://www.starlette.io/testclient/) out of an [`App`](/api/applications.md#App) instance. Additional arguments are passed to the `TestClient` constructor.

[requests]: http://docs.python-requests.org/en/master/

```python
from bocadillo import App
from bocadillo.testing import create_client

app = App()
client = create_client(app)
```

The returned `TestClient` exposes the same interface as the [requests] library, and has other useful features such as WebSocket testing helpers.

We recommend you read the documentation for Starlette's test client for further information.

### Running a live server

If you need to perform integration tests against a live server, the [`LiveServer`](/api/testing.md#liveserver) context manager should come handy. It runs `app.run()` in a separate process which is terminated when exiting the context.

```python
from bocadillo import App
from bocadillo.testing import LiveServer

app = App()

with LiveServer(app) as server:
    print(server.url)
    ...
```

### Miscellaneous utilities

#### Overriding environment variables

If you need to override some environment variables during your tests, you may find the [`override_env`](/api/utils.md#override-env) helper useful:

```python
from bocadillo.utils import override_env

with override_env("APP_ENV", "testing"):
    ...
```

## Using pytest

This section lists what we believe to be best practices when testing Bocadillo applications using the [pytest] test framework.

[pytest]: https://docs.pytest.org

### Fixtures

[fixtures]: https://docs.pytest.org/en/latest/fixture.html

When using pytest, we recommend you setup some [fixtures] that provision to application instance, a [test client](#test-client) and a [live server](#running-a-live-server). By doing so, you'll be able to write tests in a more concise fashion.

You can use this sample `conftest.py` as a starting point:

```python
# conftest.py
import pytest
from bocadillo.testing import create_client, LiveServer

from app import app


@pytest.fixture
def app():
    return app

@pytest.fixture
def client(app):
    return create_client(app)

@pytest.fixture
def server(app):
    with LiveServer(app) as server:
        yield server
```

Example test:

```python
# tests.py

def test_hello(client):
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.text = "Hello, pytest!"
```

### Testing asynchronous code

[pytest-asyncio]: https://github.com/pytest-dev/pytest-asyncio

You can use the [pytest-asyncio] extension if you need to test asynchronous code. Among other things, it provides an `asyncio` mark that allows to run `async` test functions, as well as the ability to write async fixtures.

```python
# tests.py
import pytest

from myproject import some_async_function

@pytest.mark.asyncio
async def test_render():
    result = await some_async_function()
    ...
```

[pytest]: https://pytest.org
[unittest]: https://docs.python.org/3/library/unittest.html
