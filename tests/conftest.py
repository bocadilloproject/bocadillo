from contextlib import contextmanager
from multiprocessing import Process, Event
from random import randint
from typing import NamedTuple

import pytest

from bocadillo import App, API, Templates, Recipe
from bocadillo.testing import create_client


# Tests that use the `app` fixture will run once for each of these
# application classes.
APP_CLASSES = [App, API, lambda: Recipe("tacos")]
CLIENT_FACTORIES = [create_client, lambda app: app.client]


@pytest.fixture(params=APP_CLASSES, name="app")
def fixture_app(request):
    cls = request.param
    return cls()


@pytest.fixture(params=CLIENT_FACTORIES)
def client(app, request):
    factory = request.param
    return factory(app)


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


# TODO: move to a public `testing` module.


class Server(NamedTuple):
    host: str
    port: str

    @property
    def url(self):
        return f"http://{self.host}:{self.port}"


@pytest.fixture
def create_server():
    ready = Event()
    ready_timeout = 1
    stop_timeout = 1
    host = "127.0.0.1"
    port = randint(3000, 9000)

    @contextmanager
    def _create_server(app):
        def target():
            async def callback_notify():
                # Run periodically by the Uvicorn server.
                ready.set()

            app.run(host=host, port=port, callback_notify=callback_notify)

        process = Process(target=target)
        process.start()
        if not ready.wait(ready_timeout):
            raise TimeoutError(
                f"Live server not ready after {ready_timeout} seconds"
            )

        try:
            yield Server(host=host, port=port)
        finally:
            process.terminate()
            process.join(stop_timeout)
            if process.exitcode is None:
                raise TimeoutError(
                    f"Live server still running after {stop_timeout} seconds."
                )

    return _create_server
