import pytest

from bocadillo import configure, create_client, settings


def test_basic(raw_app):
    def use_foo(app):
        @app.route("/foo")
        async def foo(req, res):
            res.text = "Foo"

    app = configure(raw_app, plugins=[use_foo])
    client = create_client(app)

    r = client.get("/foo")
    assert r.status_code == 200
    assert r.text == "Foo"


def test_use_settings(raw_app):
    def use_hello(app):
        hello_message = getattr(settings, "HELLO_MESSAGE")

        @app.route("/hello")
        async def foo(req, res):
            res.text = hello_message

    app = configure(
        raw_app, plugins=[use_hello], hello_message="Hello, plugins!"
    )
    client = create_client(app)

    r = client.get("/hello")
    assert r.status_code == 200
    assert r.text == "Hello, plugins!"


@pytest.mark.parametrize("should_use", (True, False))
def test_conditional_plugin(raw_app, should_use):
    used = False

    def use_hello(_):
        nonlocal used
        used = True

    configure(raw_app, plugins=[{use_hello: should_use}])
    assert used is should_use
