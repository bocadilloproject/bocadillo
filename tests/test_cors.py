from bocadillo import configure, create_client


def test_no_allowed_origins_by_default(raw_app):
    app = configure(raw_app, cors=True)

    @app.route("/")
    async def index(req, res):
        pass

    client = create_client(app)
    response = client.options(
        "/",
        headers={
            "origin": "foobar.com",
            "access-control-request-method": "GET",
        },
    )
    assert response.status_code == 400


def test_if_origin_not_in_allow_origins_then_400(raw_app):
    app = configure(raw_app, cors={"allow_origins": ["foobar.com"]})

    @app.route("/")
    async def index(req, res):
        pass

    client = create_client(app)
    response = client.options(
        "/",
        headers={
            "origin": "foobar.com",
            "access-control-request-method": "GET",
        },
    )
    assert response.status_code == 200

    response = client.options(
        "/",
        headers={
            "origin": "example.com",
            "access-control-request-method": "GET",
        },
    )
    assert response.status_code == 400


def test_if_method_not_in_allow_methods_then_400(raw_app):
    app = configure(
        raw_app,
        cors={"allow_origins": ["foobar.com"], "allow_methods": ["POST"]},
    )

    @app.route("/")
    async def index(req, res):
        pass

    client = create_client(app)
    response = client.options(
        "/",
        headers={
            "origin": "foobar.com",
            "access-control-request-method": "GET",
        },
    )
    assert response.status_code == 400
