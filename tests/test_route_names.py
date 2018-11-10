import pytest

from bocadillo import API
from bocadillo.exceptions import HTTPError


def test_if_no_route_exists_for_name_then_url_for_raises_404(api: API):
    @api.route('/about')
    async def about(req, res):
        pass

    with pytest.raises(HTTPError):
        api.url_for(name='about')


def test_if_route_exists_then_url_for_returns_full_path(api: API):
    @api.route('/about/{who}', name='about-someone')
    async def about(req, res, who):
        pass

    url = api.url_for('about-someone', who='me')
    assert url == '/about/me'


def test_url_for_can_be_used_in_templates(api: API):
    @api.route('/about/{who}', name='about-someone')
    async def about(req, res, who):
        pass

    @api.route('/')
    async def index(req, res):
        template = '{{ url_for("about-someone", who=who) }}'
        res.html = await api.template_string(template, who='me')

    response = api.client.get('/')
    assert response.status_code == 200
    assert response.text == '/about/me'


def test_on_class_based_views(api: API):
    @api.route('/about/{who}', name='about-someone')
    class About:
        pass

    url = api.url_for('about-someone', who='Godzilla')
    assert url == '/about/Godzilla'
