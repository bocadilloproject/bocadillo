from bocadillo import App


def test_access_sub_route(app: App):
    other = App()

    @other.route("/foo")
    async def foo(req, res):
        res.text = "OK"

    app.mount("/other", other)

    r = app.client.get("/other/foo")
    assert r.status_code == 200
    assert r.text == "OK"
