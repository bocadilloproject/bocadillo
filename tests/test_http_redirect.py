from bocadillo import App, Redirect


def _setup_views_with_redirect(app, permanent: bool = None, **kwargs):
    @app.route("/home")
    async def home(req, res):
        res.text = "You are home!"

    @app.route("/")
    async def index(req, res):
        if permanent:
            raise Redirect(permanent=True, **kwargs)
        raise Redirect(**kwargs)


def test_redirection_is_temporary_by_default(app: App, client):
    _setup_views_with_redirect(app, url="https://www.google.com")
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 302


def test_permanent_redirect(app: App, client):
    _setup_views_with_redirect(
        app, permanent=True, url="https://www.google.com"
    )
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 301


def test_redirect_to_internal_url(app: App, client):
    @app.route("/about/{who}")
    async def about(req, res, who):
        res.text = who

    @app.route("/")
    async def index(req, res):
        raise Redirect("/about/me")

    response = client.get("/")
    assert response.status_code == 200
    assert response.text == "me"


def test_if_redirect_to_non_matching_internal_url_then_404(app: App, client):
    @app.route("/")
    async def index(req, res):
        raise Redirect("/about/me")

    response = client.get("/")
    assert response.status_code == 404


def test_redirect_to_external_url(app: App, client):
    external_url = "https://httpbin.org/status/202"

    @app.route("/")
    async def index(req, res):
        raise Redirect(external_url)

    # NOTE: cannot follow redirect here, because the TestClient
    # prepends the base_url (http://testserver) to any request made, including
    # the redirected request.
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == external_url
