import pytest

from bocadillo import App, HTTPError


def test_access_sub_route(app: App):
    other = App()

    @other.route("/foo")
    async def foo(req, res):
        pass

    app.mount("/other", other)

    r = app.client.get("/other/foo")
    assert r.status_code == 200


@pytest.mark.parametrize("with_name", (True, False))
def test_url_for(app: App, with_name: bool):
    other = App("other" if with_name else None)

    @other.route("/foo")
    async def foo(req, res):
        pass

    app.mount("/other", other)

    if with_name:
        assert app.url_for("other:foo") == "/other/foo"
    else:
        with pytest.raises(HTTPError):
            app.url_for("other:foo")
