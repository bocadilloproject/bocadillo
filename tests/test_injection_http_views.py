import pytest

from bocadillo import App, provider


@pytest.fixture(autouse=True)
async def hello_provider():
    @provider
    async def hello_format():
        return "Hello, {who}!"

    @provider
    async def hello(hello_format) -> str:
        return hello_format.format(who="providers")


def test_function_based_view(app: App, client):
    @app.route("/hi")
    async def say_hi(req, res, hello):
        res.text = hello

    r = client.get("/hi")
    assert r.status_code == 200
    assert r.text == "Hello, providers!"


def test_function_based_view_with_route_parameters(app: App, client):
    @app.route("/hi/{who}")
    async def say_hi(req, res, hello_format, who):
        res.text = hello_format.format(who=who)

    r = client.get("/hi/peeps")
    assert r.status_code == 200
    assert r.text == "Hello, peeps!"


def test_class_based_view(app: App, client):
    @app.route("/hi")
    class SayHi:
        async def get(self, req, res, hello):
            res.text = hello

    r = client.get("/hi")
    assert r.status_code == 200
    assert r.text == "Hello, providers!"


def test_class_based_view_with_route_parameters(app: App, client):
    @app.route("/hi/{who}")
    class SayHi:
        async def get(self, req, res, hello_format, who):
            res.text = hello_format.format(who=who)

    r = client.get("/hi/peeps")
    assert r.status_code == 200
    assert r.text == "Hello, peeps!"
