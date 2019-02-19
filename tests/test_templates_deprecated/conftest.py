from typing import NamedTuple

import pytest

from bocadillo import App


class TemplateWrapper(NamedTuple):
    name: str
    context: dict
    rendered: str
    source_directory: str


def _create_template(app, tmpdir_factory, dirname):
    templates_dir = tmpdir_factory.mktemp(dirname)
    template_file = templates_dir.join("hello.html")
    template_file.write("<h1>Hello, {{ name }}!</h1>")
    app.templates_dir = str(templates_dir)
    return TemplateWrapper(
        name="hello.html",
        context={"name": "Bocadillo"},
        rendered="<h1>Hello, Bocadillo!</h1>",
        source_directory=dirname,
    )


@pytest.fixture
def template_file(app: App, tmpdir_factory):
    return _create_template(app, tmpdir_factory, dirname="templates")


@pytest.fixture
def template_file_elsewhere(app: App, tmpdir_factory):
    return _create_template(app, tmpdir_factory, dirname="templates_elsewhere")
