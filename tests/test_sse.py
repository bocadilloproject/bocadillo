from multiprocessing import Value
from time import sleep

import pytest
import requests

from bocadillo import App, ClientDisconnect, LiveServer, server_event

from .utils import stops_incrementing


@pytest.mark.parametrize(
    "args, kwargs, lines",
    [
        [(), {"data": "hello"}, ["data: hello", ""]],
        [(), {"data": "hello", "id": 1}, ["id: 1", "data: hello", ""]],
        [
            ("foo",),
            {"id": 1, "data": "hello"},
            ["id: 1", "event: foo", "data: hello", ""],
        ],
        [
            ("foo",),
            {"id": 1, "json": {"message": "hello"}},
            ["id: 1", "event: foo", 'data: {"message": "hello"}', ""],
        ],
        [(), {"data": ["hello", "world"]}, ["data: hello", "data: world", ""]],
    ],
)
def test_send_event(app: App, client, args: list, kwargs: dict, lines: list):
    @app.route("/events")
    async def view_with_events(req, res):
        @res.event_stream
        async def generate_events():
            yield server_event(*args, **kwargs)

    r = client.get("/events", stream=True)
    assert r.status_code == 200
    stream = r.iter_lines()

    received = [next(stream).decode() for _ in lines]
    assert received == lines

    with pytest.raises(StopIteration):
        next(stream)


def test_sse_headers_are_set(app: App, client):
    @app.route("/events")
    async def view_with_events(req, res):
        @res.event_stream
        async def generate_events():
            yield server_event(name="foo")

    r = client.get("/events")
    assert r.status_code == 200
    assert r.headers["connection"] == "keep-alive"
    assert r.headers["content-type"] == "text/event-stream"
    assert r.headers["cache-control"] == "no-cache"


def test_cache_control_header_not_replaced_if_manually_set(app: App, client):
    @app.route("/events")
    async def sse(req, res):
        res.headers["cache-control"] = "foo"

        @res.event_stream
        async def generate_events():
            yield server_event("hello")

    r = client.get("/events")
    assert r.status_code == 200
    assert r.headers["cache-control"] == "foo"


def test_stop_on_client_disconnect(app: App):
    num_sent = Value("i", 0)

    @app.route("/events")
    async def sse(req, res):
        @res.event_stream
        async def events():
            nonlocal num_sent
            while True:
                yield server_event("hello")
                num_sent.value += 1

    with LiveServer(app) as server:
        r = requests.get(f"{server.url}/events", stream=True)
        assert r.status_code == 200
        assert stops_incrementing(counter=num_sent, response=r)


def test_raise_client_disconnects(app: App):
    caught = Value("i", 0)

    @app.route("/events")
    async def sse(req, res):
        @res.event_stream(raise_on_disconnect=True)
        async def events():
            nonlocal caught
            try:
                while True:
                    yield server_event("hello")
            except ClientDisconnect:
                caught.value = 1

    with LiveServer(app) as server:
        r = requests.get(f"{server.url}/events", stream=True)
        assert r.status_code == 200
        r.close()
        sleep(0.1)
        assert caught.value
