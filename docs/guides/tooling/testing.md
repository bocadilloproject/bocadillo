# Testing

This page documents ways in which Bocadillo can help you write great tests and ensure the quality of your apps.

We also have specific how-to guides explaining how to integrate Bocadillo with your favorite test framework:

- [pytest](/how-to/test-pytest.md)

## Test client

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

## Live server

If you need to perform integration tests against a live server, the [`LiveServer`](/api/testing.md#liveserver) context manager should come handy. It runs `app.run()` in a separate process which is terminated when exiting the context.

```python
from bocadillo import App
from bocadillo.testing import LiveServer

app = App()

with LiveServer(app) as server:
    print(server.url)
    ...
```

## Miscellaneous utilities

### Overriding environment variables

If you need to override some environment variables during your tests, you may find the [`override_env`](/api/utils.md#override-env) helper useful:

```python
from bocadillo.utils import override_env

with override_env("APP_ENV", "testing"):
    ...
```
