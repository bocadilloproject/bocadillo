import pytest

from bocadillo import API


def test_root_wildcard(api: API):
    @api.route("{}")
    async def root(req, res):
        res.text = "root"

    r = api.client.get("/")
    assert r.status_code == 200
    assert r.text == "root"


def test_wildcard(api: API):
    @api.route("/foo/{}-bar")
    async def foo_bar(req, res):
        # Field has no name => not passed as a parameter to view.
        # NOTE: if user wants to retrieve the value of the matched field,
        # they must give it a name.
        pass

    r = api.client.get("/foo/no-bar")
    assert r.status_code == 200


def test_if_wildcard_first_then_other_routes_wont_match(api: API):
    @api.route("/foo/{}")
    async def foo_all(req, res):
        res.text = "all"

    @api.route("/foo/bar")
    async def foo_bar(req, res):
        res.text = "bar"

    r = api.client.get("/foo/bar")
    assert r.status_code == 200
    assert r.text == "all"


@pytest.mark.parametrize(
    "path, text", [("/foo/bar", "bar"), ("/foo/jong", "all")]
)
def test_if_wildcard_last_then_matches_by_default(
    api: API, path: str, text: str
):
    @api.route("/foo/bar")
    async def foo_bar(req, res):
        res.text = "bar"

    @api.route("/foo/{}")
    async def foo_all(req, res):
        res.text = "all"

    r = api.client.get(path)
    assert r.status_code == 200
    assert r.text == text
