import pytest

from bocadillo import API, HTTPError
from bocadillo.views import view


def test_if_no_route_exists_for_name_then_url_for_raises_404(api: API):
    with pytest.raises(HTTPError):
        api.url_for(name="about")


def test_if_route_exists_then_url_for_returns_full_path(api: API):
    @api.route("/about/{who}")
    class About:
        async def get(self, req, res, who):
            pass

    url = api.url_for("about", who="me")
    assert url == "/about/me"


def test_name_can_be_explicitly_given(api: API):
    @api.route("/about/{who}", name="about-someone")
    class About:
        async def get(self, req, res, who):
            pass

    with pytest.raises(HTTPError):
        api.url_for(name="about", who="me")

    url = api.url_for("about-someone", who="me")
    assert url == "/about/me"


def test_url_for_can_be_used_in_templates(api: API):
    @api.route("/about/{who}")
    class About:
        async def get(self, req, res, who):
            pass

    @api.route("/")
    class Index:
        async def get(self, req, res):
            template = "{{ url_for('about', who=who) }}"
            res.html = api.template_string(template, who="me")

    response = api.client.get("/")
    assert response.status_code == 200
    assert response.text == "/about/me"


def test_on_name_is_inferred_from_view_name(api: API):
    @api.route("/about/{who}")
    class AboutPerson:
        async def get(self, req, res, who):
            pass

    url = api.url_for("about_person", who="Godzilla")
    assert url == "/about/Godzilla"


def test_on_function_view(api: API):
    @api.route("/about/{who}")
    @view()
    async def about_person(req, res, who):
        pass

    url = api.url_for("about_person", who="Godzilla")
    assert url == "/about/Godzilla"


def test_use_namespace(api: API):
    @api.route("/about", namespace="blog")
    class About:
        async def get(self, req, res):
            pass

    url = api.url_for("blog:about")
    assert url == "/about"
