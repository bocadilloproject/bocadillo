import pytest

from bocadillo import settings, configure, create_client, plugin
from bocadillo.plugins import _PLUGINS


INITIAL_PLUGINS = dict(_PLUGINS)


@pytest.fixture(autouse=True)
def reset_plugins():
    yield
    _PLUGINS.clear()
    for name, value in INITIAL_PLUGINS.items():
        _PLUGINS[name] = value


def test_basic(raw_app):
    @plugin
    def use_foo(app):
        @app.route("/foo")
        async def foo(req, res):
            res.text = "Foo"

    app = configure(raw_app)
    client = create_client(app)

    r = client.get("/foo")
    assert r.status_code == 200
    assert r.text == "Foo"


def test_use_settings(raw_app):
    @plugin
    def use_hello(app):
        hello_message = getattr(settings, "HELLO_MESSAGE")

        @app.route("/hello")
        async def foo(req, res):
            res.text = hello_message

    app = configure(raw_app, hello_message="Hello, plugins!")
    client = create_client(app)

    r = client.get("/hello")
    assert r.status_code == 200
    assert r.text == "Hello, plugins!"
