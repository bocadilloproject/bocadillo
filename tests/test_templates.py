import pytest

from bocadillo import API
from bocadillo.exceptions import TemplateNotFound
from tests.conftest import TemplateWrapper


def test_render_sync(template_file: TemplateWrapper, api: API):
    @api.route('/')
    def index(req, res):
        res.html = api.template(
            template_file.name,
            **template_file.context,
        )

    response = api.client.get('/')
    assert response.status_code == 200
    assert response.text == template_file.rendered


def test_render_async(template_file: TemplateWrapper, api: API):
    @api.route('/')
    async def index(req, res):
        res.html = await api.template_async(
            template_file.name,
            **template_file.context,
        )

    response = api.client.get('/')
    assert response.status_code == 200
    assert response.text == template_file.rendered


def test_if_template_does_not_exist_then_template_not_found_raised(api: API):
    @api.route('/')
    def index(req, res):
        res.html = api.template('doesnotexist.html')

    with pytest.raises(TemplateNotFound):
        api.client.get('/')
