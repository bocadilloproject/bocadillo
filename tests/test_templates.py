import pytest
from jinja2.exceptions import TemplateNotFound

from bocadillo import API
from tests.conftest import TemplateWrapper


@pytest.mark.asyncio
async def test_render(template_file: TemplateWrapper, api: API):
    html = await api.template(template_file.name, **template_file.context)
    assert html == template_file.rendered


@pytest.mark.asyncio
async def test_render_using_dict(template_file: TemplateWrapper, api: API):
    html = await api.template(template_file.name, template_file.context)
    assert html == template_file.rendered


def test_render_sync(template_file: TemplateWrapper, api: API):
    html = api.template_sync(template_file.name, **template_file.context)
    assert html == template_file.rendered


@pytest.mark.asyncio
async def test_modify_templates_dir(
    template_file_elsewhere: TemplateWrapper, api: API
):
    html = await api.template(
        template_file_elsewhere.name, **template_file_elsewhere.context
    )
    assert html == template_file_elsewhere.rendered


@pytest.mark.asyncio
async def test_if_template_does_not_exist_then_not_found_raised(api: API):
    with pytest.raises(TemplateNotFound):
        await api.template("doesnotexist.html")


def test_render_by_template_string(api: API):
    html = api.template_string("<h1>{{ title }}</h1>", title="Hello")
    assert html == "<h1>Hello</h1>"
