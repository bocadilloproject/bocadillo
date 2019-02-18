from typing import NamedTuple

import pytest

from bocadillo import API


class TemplateWrapper(NamedTuple):
    name: str
    context: dict
    rendered: str
    source_directory: str


def _create_template(api, tmpdir_factory, dirname):
    templates_dir = tmpdir_factory.mktemp(dirname)
    template_file = templates_dir.join("hello.html")
    template_file.write("<h1>Hello, {{ name }}!</h1>")
    api.templates_dir = str(templates_dir)
    return TemplateWrapper(
        name="hello.html",
        context={"name": "Bocadillo"},
        rendered="<h1>Hello, Bocadillo!</h1>",
        source_directory=dirname,
    )


@pytest.fixture
def template_file(api: API, tmpdir_factory):
    return _create_template(api, tmpdir_factory, dirname="templates")


@pytest.fixture
def template_file_elsewhere(api: API, tmpdir_factory):
    return _create_template(api, tmpdir_factory, dirname="templates_elsewhere")
