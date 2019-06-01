import pytest
from bocadillo import App
from jinja2.exceptions import TemplateNotFound

from bocadillo import Templates

from .conftest import TemplateWrapper, create_template


@pytest.mark.asyncio
async def test_render(template_file: TemplateWrapper, templates: Templates):
    html = await templates.render(template_file.name, **template_file.context)
    assert html == template_file.rendered


@pytest.mark.asyncio
async def test_render_using_dict(
    template_file: TemplateWrapper, templates: Templates
):
    html = await templates.render(template_file.name, template_file.context)
    assert html == template_file.rendered


def test_render_sync(template_file: TemplateWrapper, templates: Templates):
    html = templates.render_sync(template_file.name, **template_file.context)
    assert html == template_file.rendered


def test_render_string(templates: Templates):
    html = templates.render_string("<h1>{{ title }}</h1>", title="Hello")
    assert html == "<h1>Hello</h1>"


@pytest.mark.asyncio
async def test_modify_templates_dir(templates: Templates, tmpdir_factory):
    template = create_template(templates, tmpdir_factory, dirname="elsewhere")
    html = await templates.render(template.name, **template.context)
    assert html == template.rendered


def test_modify_context():
    templates = Templates(context={"initial": "stuff"})
    templates.context = {"key": "value"}
    templates.context["foo"] = "bar"
    assert (
        templates.render_string("{{ foo }}, {{ key }} and {{ initial }}")
        == "bar, value and "
    )


@pytest.mark.asyncio
async def test_if_template_does_not_exist_then_not_found_raised(
    templates: Templates
):
    with pytest.raises(TemplateNotFound):
        await templates.render("doesnotexist.html")
