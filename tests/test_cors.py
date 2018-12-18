from bocadillo import API


def test_no_allowed_origins_by_default():
    api = API(enable_cors=True)

    @api.route("/")
    async def index(req, res):
        pass

    response = api.client.options(
        "/",
        headers={
            "origin": "foobar.com",
            "access-control-request-method": "GET",
        },
    )
    assert response.status_code == 400


def test_if_origin_not_in_allow_origins_then_400():
    api = API(enable_cors=True, cors_config={"allow_origins": ["foobar.com"]})

    @api.route("/")
    async def index(req, res):
        pass

    response = api.client.options(
        "/",
        headers={
            "origin": "foobar.com",
            "access-control-request-method": "GET",
        },
    )
    assert response.status_code == 200

    response = api.client.options(
        "/",
        headers={
            "origin": "example.com",
            "access-control-request-method": "GET",
        },
    )
    assert response.status_code == 400


def test_if_method_not_in_allow_methods_then_400():
    api = API(
        enable_cors=True,
        cors_config={
            "allow_origins": ["foobar.com"],
            "allow_methods": ["POST"],
        },
    )

    @api.route("/")
    async def index(req, res):
        pass

    response = api.client.options(
        "/",
        headers={
            "origin": "foobar.com",
            "access-control-request-method": "GET",
        },
    )
    assert response.status_code == 400
