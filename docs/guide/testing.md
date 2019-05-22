# Testing

One of the design principles of Bocadillo is to make it easy to write high-quality applications. This includes helping you write great tests and ensure the quality of your apps.

::: tip
We wrote specific how-to guides on integrating Bocadillo with the following test frameworks:

- [pytest](/how-to/test-pytest.md)

:::

## Test client

The [`create_client`](/api/testing.md#create-client) helper can be used to build a [Starlette `TestClient`](https://www.starlette.io/testclient/) out of an [`App`](/api/applications.md#App) instance. Additional arguments are passed to the `TestClient` constructor.

[requests]: http://docs.python-requests.org/en/master/

```python
from bocadillo import App, create_client

app = App()
client = create_client(app)
```

The returned `TestClient` exposes the same interface as the [requests] library, and has other useful features such as WebSocket testing helpers.

We recommend you read the documentation for Starlette's test client for further information.

## Live server

If you need to perform integration tests against a live server, the [`LiveServer`](/api/testing.md#liveserver) context manager should come handy. It starts a [uvicorn server](/guide/apps.md#serving-an-application) in a separate process, and terminates it when exiting the context. You can then make requests to it, e.g. using [requests]:

```python
import requests
from bocadillo import App, configure, LiveServer

app = App()
configure(app)

with LiveServer(app) as server:
    response = requests.get(server.url("/foo"))
```

## Miscellaneous utilities

### Overriding environment variables

If you need to override some environment variables during your tests, you may find the [`override_env`](/api/utils.md#override-env) helper useful:

```python
from bocadillo.utils import override_env

with override_env("APP_ENV", "testing"):
    ...
```
