import os
import random
from multiprocessing import Event, Process
from typing import TYPE_CHECKING

from starlette.testclient import TestClient

try:
    import pytest
except ImportError:
    pytest = None

if TYPE_CHECKING:
    from .applications import App


def create_client(app: "App", **kwargs) -> TestClient:
    """Create a [Starlette Test Client][client] out of an application.

    [client]: https://www.starlette.io/testclient/

    # Parameters
    app: an #::bocadillo.applications#App instance.
    **kwargs (any): keyword arguments passed to the `TestClient` constructor.

    # Returns
    client (TestClient): a Starlette test client.
    """
    return TestClient(app, **kwargs)


class LiveServer:
    """Context manager to spin up a live server in a separate process.

    The server process is terminated when exiting the context.

    # Parameters
    app: an #::bocadillo.applications#App instance.
    host (str):
        the host to run the server on.
        Defaults to `"127.0.0.1."` (i.e. `localhost`).
    port (int):
        the port to run the server on.
        Defaults to a random integer between 3000 and 9000.
    ready_timeout (float):
        The maximum time to wait for the live server to be ready to handle
        connections, in seconds.
        Defaults to 5.
    stop_timeout (float):
        The maximum time to wait for the live server to terminate, in seconds.
        Defaults to 5.
    
    # Attributes
    url (str):
        the full URL where the server lives.
    """

    def __init__(
        self,
        app: "App",
        host: str = "127.0.0.1",
        port: int = None,
        ready_timeout: float = 5,
        stop_timeout: float = 5,
    ):
        if (
            pytest is not None and os.getenv("CI") and os.getenv("TRAVIS")
        ):  # pragma: no cover
            pytest.skip("live server process sometimes makes travis ci stall")

        if port is None:
            port = random.randint(3000, 9000)

        self.app = app
        self.host = host
        self.port = port
        self.ready_timeout = ready_timeout
        self.stop_timeout = stop_timeout
        self._process: Process = None

    @property
    def url(self):
        return f"http://{self.host}:{self.port}"

    def __enter__(self):
        ready = Event()

        def target():
            async def callback_notify():
                # Run periodically by the Uvicorn server.
                ready.set()

            self.app.run(
                host=self.host, port=self.port, callback_notify=callback_notify
            )

        self._process = Process(target=target)
        self._process.start()

        if not ready.wait(self.ready_timeout):  # pragma: no cover
            raise TimeoutError(
                f"Live server not ready after {self.ready_timeout} seconds"
            )

        return self

    def __exit__(self, *args):
        self._process.terminate()
        self._process.join(self.stop_timeout)
        if self._process.exitcode is None:  # pragma: no cover
            raise TimeoutError(
                f"Live server still running after {self.stop_timeout} seconds."
            )
