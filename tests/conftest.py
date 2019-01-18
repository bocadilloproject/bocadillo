import json
from typing import NamedTuple
from multiprocessing import Process
from time import sleep

import pytest
from click.testing import CliRunner

from bocadillo import API


@pytest.fixture
def api():
    _api = API()
    _websocket_connect = _api.client.websocket_connect

    def websocket_connect(url, *args, **kwargs):
        session = _websocket_connect(url, *args, **kwargs)
        # Receives bytes by default
        session.receive_json = lambda: json.loads(session.receive_text())
        # Sends bytes by default
        session.send_json = lambda value: session.send_text(json.dumps(value))
        return session

    _api.client.websocket_connect = websocket_connect
    return _api


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


@pytest.fixture
def runner():
    return CliRunner()


class Server(Process):
    # Run the API in a separate process.

    def __init__(self, api):
        super().__init__(target=api.run)

    def start(self):
        super().start()
        sleep(0.5)

    def close(self):
        self.terminate()
        while self.is_alive():
            sleep(0.1)
        super().close()


@pytest.fixture(scope="function")
def server(api: API):
    s = Server(api)
    yield s
    s.close()
