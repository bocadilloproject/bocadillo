import pytest

from bocadillo import App


def _setup_views_with_redirect(app, permanent: bool = None, **kwargs):
    @app.route("/home")
    async def home(req, res):
        res.text = "You are home!"

    @app.route("/")
    async def index(req, res):
        if permanent:
            app.redirect(permanent=True, **kwargs)
        else:
            app.redirect(**kwargs)


def test_redirect_by_route_name(app: App, client):
    _setup_views_with_redirect(app, name="home")
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == "You are home!"


def test_if_redirect_to_non_existing_route_then_404(app: App, client):
    _setup_views_with_redirect(app, name="about")
    response = client.get("/")
    assert response.status_code == 404


def test_redirection_is_temporary_by_default(app: App, client):
    _setup_views_with_redirect(app, name="home")
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 302


def test_permanent_redirect(app: App, client):
    _setup_views_with_redirect(app, permanent=True, name="home")
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 301


def test_at_least_one_of_name_or_url_must_be_given(app: App):
    with pytest.raises(AssertionError) as ctx:
        app.redirect()
    assert all(item in str(ctx.value) for item in ("url", "expected", "name"))


def test_redirect_to_internal_url(app: App, client):
    @app.route("/about/{who}")
    async def about(req, res, who):
        res.text = who

    @app.route("/")
    async def index(req, res):
        app.redirect(url="/about/me")

    response = client.get("/")
    assert response.status_code == 200
    assert response.text == "me"


def test_if_redirect_to_non_matching_internal_url_then_404(app: App, client):
    @app.route("/")
    async def index(req, res):
        app.redirect(url="/about/me")

    response = client.get("/")
    assert response.status_code == 404


def test_redirect_to_external_url(app: App, client):
    external_url = "https://httpbin.org/status/202"

    @app.route("/")
    async def index(req, res):
        app.redirect(url=external_url)

    # NOTE: cannot follow redirect here, because the TestClient
    # prepends the base_url (http://testserver) to any request made, including
    # the redirected request.
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == external_url
