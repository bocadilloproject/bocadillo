# Testing with `pytest`

This page lists what we believe are best practices when testing Bocadillo applications using the [pytest] test framework.

[pytest]: https://docs.pytest.org

## Fixtures

[fixtures]: https://docs.pytest.org/en/latest/fixture.html

When using pytest, we recommend you setup some [fixtures] to provision an [application instance](/guide/apps.md), a [test client](/guide/testing.md#test-client) and a [live server](/guide/testing.md#live-server). By doing so, you'll be able to write tests in a more concise fashion.

You can use this sample `conftest.py` as a starting point:

```python
# conftest.py
import pytest
from bocadillo import configure, create_client, LiveServer

from app import app

configure(app)

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

## Testing asynchronous code

[pytest-asyncio]: https://github.com/pytest-dev/pytest-asyncio

You can use the [pytest-asyncio] extension if you need to test asynchronous code.

Among other things, it provides an `asyncio` mark that allows to run `async` test functions, as well as the ability to write async fixtures.

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
