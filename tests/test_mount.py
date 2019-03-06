from bocadillo import App


def test_access_sub_route(app: App, client):
    other = App()

    @other.route("/foo")
    async def foo(req, res):
        res.text = "OK"

    app.mount("/other", other)

    r = client.get("/other/foo")
    assert r.status_code == 200
    assert r.text == "OK"
