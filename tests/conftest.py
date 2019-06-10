import typing

import pytest

from bocadillo import App, configure, create_client, Templates, settings


@pytest.fixture(name="raw_app")
def fixture_raw_app(request) -> App:
    settings._clear()
    return App()


@pytest.fixture(name="app")
def fixture_app(raw_app: App) -> App:
    configure(raw_app)
    return raw_app


@pytest.fixture
def client(app):
    return create_client(app)


@pytest.fixture(name="templates")
def fixture_templates():
    return Templates()


class TemplateWrapper(typing.NamedTuple):
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
