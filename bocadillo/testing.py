import random
from contextlib import contextmanager
from multiprocessing import Event, Process
from typing import TYPE_CHECKING, NamedTuple

from starlette.testclient import TestClient

if TYPE_CHECKING:
    from .applications import App


def create_client(app: "App", **kwargs) -> TestClient:
    """Create a [Starlette Test Client][client] out of an application.

    [client]: https://www.starlette.io/testclient/

    # Parameters
    app (App): an application instance.
    **kwargs (any): keyword arguments passed to the `TestClient` constructor.

    # Returns
    client (TestClient): a Starlette test client.
    """
    return TestClient(app, **kwargs)


class Server(NamedTuple):
    host: str
    port: str

    @property
    def url(self):
        return f"http://{self.host}:{self.port}"


@contextmanager
def create_server(
    app,
    host: str = "127.0.0.1",
    port: int = None,
    ready_timeout=1,
    stop_timeout=1,
):
    if port is None:
        port = random.randint(3000, 9000)

    ready = Event()

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
