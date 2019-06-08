import pytest

from bocadillo import App


@pytest.mark.parametrize("path", ["/other", "/other/foo"])
def test_mount(app: App, client, path):
    other = App()

    requested_path = None

    async def view(req, res):
        nonlocal requested_path
        requested_path = req.url.path

    other.route("/")(view)
    other.route("/foo")(view)

    app.mount("/other", other)

    r = client.get(path)
    assert r.status_code == 200
    assert requested_path is not None
    assert requested_path.rstrip("/") == path


def test_mount_route_parameter(app, client):
    other = App()

    @other.route("/items/{pk}")
    async def get_item(req, res, pk: int):
        res.json = {"pk": pk}

    app.mount("/other", other)

    r = client.get("/other/items/12")
    assert r.json() == {"pk": 12}
