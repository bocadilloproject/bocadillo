import pytest

from bocadillo import App, HTTPError


def test_if_no_route_exists_for_name_then_url_for_raises_404(app: App):
    with pytest.raises(HTTPError):
        app.url_for(name="about")


def test_if_route_exists_then_url_for_returns_full_path(app: App):
    @app.route("/about/{who}")
    async def about(req, res, who):
        pass

    url = app.url_for("about", who="me")
    assert url == "/about/me"


def test_name_can_be_explicitly_given(app: App):
    @app.route("/about/{who}", name="about-someone")
    async def about(req, res, who):
        pass

    with pytest.raises(HTTPError):
        app.url_for(name="about", who="me")

    url = app.url_for("about-someone", who="me")
    assert url == "/about/me"


def test_name_is_inferred_from_view_name(app: App):
    @app.route("/about/{who}")
    class AboutPerson:
        async def get(self, req, res, who):
            pass

    url = app.url_for("about_person", who="Godzilla")
    assert url == "/about/Godzilla"

    @app.route("/about/{who}")
    async def about_who(req, res, who):
        pass

    url = app.url_for("about_who", who="Godzilla")
    assert url == "/about/Godzilla"


def test_if_route_has_namespace_then_must_be_used_when_reversing(app: App):
    @app.route("/about", namespace="blog")
    async def about(req, res):
        pass

    assert app.url_for("blog:about") == "/about"

    with pytest.raises(HTTPError):
        app.url_for("about")


def test_reverse_named_sub_app_route(app: App):
    sub = App("sub")

    @sub.route("/foo")
    async def foo(req, res):
        pass

    app.mount("/sub", sub)

    assert app.url_for("sub:foo") == "/sub/foo"


def test_cannot_reverse_unnamed_sub_app_route(app: App):
    sub = App()

    @sub.route("/foo")
    async def foo(req, res):
        pass

    app.mount("/sub", sub)

    with pytest.raises(HTTPError):
        app.url_for("sub:foo")
