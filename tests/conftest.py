import json
from typing import NamedTuple

import pytest
from click.testing import CliRunner

from bocadillo import App, API, Templates

from .utils import RouteBuilder


@pytest.fixture(params=[App, API])
def app(request):
    cls = request.param
    _app = cls()
    _websocket_connect = _app.client.websocket_connect

    def websocket_connect(url, *args, **kwargs):
        session = _websocket_connect(url, *args, **kwargs)
        # Receives bytes by default
        session.receive_json = lambda: json.loads(session.receive_text())
        # Sends bytes by default
        session.send_json = lambda value: session.send_text(json.dumps(value))
        return session

    _app.client.websocket_connect = websocket_connect
    return _app


@pytest.fixture
def builder(app: App):
    return RouteBuilder(app)


@pytest.fixture
def templates(app: App):
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


@pytest.fixture
def runner():
    return CliRunner()
