from starlette.datastructures import FormData

from bocadillo import App


def test_form_parsing(app: App):
    @app.route("/")
    async def index(req, res):
        form = await req.form()
        assert isinstance(form, FormData)
        # not actually a dict, so not immediately JSON-serializable
        res.media = dict(form)

    r = app.client.get("/", data={"foo": "bar"})
    assert r.status_code == 200
    assert r.json() == {"foo": "bar"}
