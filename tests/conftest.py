from typing import NamedTuple

import pytest

from bocadillo import App, Templates, Recipe
from bocadillo.testing import create_client


APP_CLASSES = [App, lambda: Recipe("tacos")]


@pytest.fixture(params=APP_CLASSES, name="app")
def fixture_app(request):
    cls = request.param
    return cls()


@pytest.fixture
def client(app):
    return create_client(app)


@pytest.fixture(name="templates")
def fixture_templates(app: App):
    return Templates(app)


class TemplateWrapper(NamedTuple):
    name: str
    context: dict
    rendered: str
    root: str


def create_template(
    templates: Templates, tmpdir_factory, dirname: str
) -> TemplateWrapper:
    templates_dir = tmpdir_factory.mktemp(dirname)

    template = templates_dir.join("hello.html")
    template.write("<h1>Hello, {{ name }}!</h1>")

    templates.directory = str(templates_dir)

    return TemplateWrapper(
        name="hello.html",
        context={"name": "Bocadillo"},
        rendered="<h1>Hello, Bocadillo!</h1>",
        root=str(templates_dir),
    )


@pytest.fixture
def template_file(templates: Templates, tmpdir_factory) -> TemplateWrapper:
    return create_template(templates, tmpdir_factory, dirname="templates")
