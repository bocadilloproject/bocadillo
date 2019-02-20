import pytest
from jinja2.exceptions import TemplateNotFound

from bocadillo import App

from .conftest import TemplateWrapper


@pytest.mark.asyncio
async def test_render(template_file: TemplateWrapper, app: App):
    html = await app.template(template_file.name, **template_file.context)
    assert html == template_file.rendered


@pytest.mark.asyncio
async def test_render_using_dict(template_file: TemplateWrapper, app: App):
    html = await app.template(template_file.name, template_file.context)
    assert html == template_file.rendered


def test_render_sync(template_file: TemplateWrapper, app: App):
    html = app.template_sync(template_file.name, **template_file.context)
    assert html == template_file.rendered


@pytest.mark.asyncio
async def test_modify_templates_dir(
    template_file_elsewhere: TemplateWrapper, app: App
):
    html = await app.template(
        template_file_elsewhere.name, **template_file_elsewhere.context
    )
    assert html == template_file_elsewhere.rendered


@pytest.mark.asyncio
async def test_if_template_does_not_exist_then_not_found_raised(app: App):
    with pytest.raises(TemplateNotFound):
        await app.template("doesnotexist.html")


def test_render_by_template_string(app: App):
    html = app.template_string("<h1>{{ title }}</h1>", title="Hello")
    assert html == "<h1>Hello</h1>"
