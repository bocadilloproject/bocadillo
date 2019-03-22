import pytest

from bocadillo import App, provider, useprovider


@pytest.mark.parametrize("by_name", (False, True))
def test_useprovider(app: App, client, by_name):
    called = False

    @provider
    async def set_called():
        nonlocal called
        called = True

    @app.route("/")
    @useprovider("set_called" if by_name else set_called)
    async def index(req, res):
        pass

    r = client.get("/")
    assert r.status_code == 200
    assert called
