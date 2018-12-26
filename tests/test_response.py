from bocadillo import API


def test_if_nothing_set_then_response_is_empty(api: API):
    @api.route("/")
    class Index:
        async def get(self, req, res):
            pass

    response = api.client.get("/")
    assert not response.text


def test_if_status_code_is_no_content_then_no_content_type_set(api: API):
    @api.route("/")
    class Index:
        async def get(self, req, res):
            res.status_code = 204

    response = api.client.get("/")
    assert response.status_code == 204
    assert not response.text
    assert response.headers.get("content-type") is None


def test_content_type_defaults_to_plaintext(api: API):
    @api.route("/")
    class Index:
        async def get(self, req, res):
            res.content = "Something magical"
            # make sure no content-type is set before leaving the view
            res.headers.pop("Content-Type", None)

    response = api.client.get("/")
    assert response.headers["Content-Type"] == "text/plain"


def test_if_text_set_then_response_is_plain_text(api: API):
    @api.route("/")
    class Index:
        async def get(self, req, res):
            res.text = "foo"

    response = api.client.get("/")
    assert response.headers["Content-Type"] == "text/plain"
    assert response.text == "foo"


def test_if_media_set_then_response_is_json(api: API):
    @api.route("/")
    class Index:
        async def get(self, req, res):
            res.media = {"foo": "bar"}

    response = api.client.get("/")
    assert response.json() == {"foo": "bar"}


def test_if_html_set_then_response_is_html(api: API):
    @api.route("/")
    class Index:
        async def get(self, req, res):
            res.html = "<h1>Foo</h1>"

    response = api.client.get("/")
    assert response.headers["Content-Type"] == "text/html"
    assert response.text == "<h1>Foo</h1>"


def test_last_response_setter_called_has_priority(api: API):
    @api.route("/")
    class Index:
        async def get(self, req, res):
            res.media = {"foo": "bar"}
            res.text = "foo"

    response = api.client.get("/")
    assert response.headers["Content-Type"] == "text/plain"
    assert response.text == "foo"

    @api.route("/")
    class Index:
        async def get(self, req, res):
            res.text = "foo"
            res.media = {"foo": "bar"}

    response = api.client.get("/")
    assert response.headers["Content-Type"] == "application/json"
    assert response.json() == {"foo": "bar"}
