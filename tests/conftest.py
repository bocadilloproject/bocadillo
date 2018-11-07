from typing import NamedTuple

import pytest

from bocadillo import API
from .utils import RouteBuilder


@pytest.fixture
def api():
    return API()


@pytest.fixture
def builder(api: API):
    return RouteBuilder(api)


class TemplateWrapper(NamedTuple):
    name: str
    context: dict
    rendered: str


@pytest.fixture
def template_file(api: API, tmpdir_factory):
    templates_dir = tmpdir_factory.mktemp('templates')
    template_file = templates_dir.join('hello.html')
    template_file.write('<h1>Hello, {{ name }}!</h1>')
    api.templates_dir = str(templates_dir)
    return TemplateWrapper(
        name='hello.html',
        context={'name': 'Bocadillo'},
        rendered='<h1>Hello, Bocadillo!</h1>',
    )
