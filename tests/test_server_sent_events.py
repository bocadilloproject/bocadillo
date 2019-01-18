from multiprocessing import Value

import pytest
import requests

from bocadillo import API, server_event

from .utils import stops_incrementing


@pytest.mark.parametrize(
    "args, kwargs, lines",
    [
        [("hello",), {}, ["data: hello", ""]],
        [("hello",), {"id": 1}, ["id: 1", "data: hello", ""]],
        [
            ("hello",),
            {"id": 1, "name": "foo"},
            ["id: 1", "event: foo", "data: hello", ""],
        ],
        [
            (),
            {"id": 1, "name": "foo", "json": {"message": "hello"}},
            ["id: 1", "event: foo", 'data: {"message": "hello"}', ""],
        ],
    ],
)
def test_send_event(api: API, args: list, kwargs: dict, lines: list):
    @api.route("/events")
    async def view_with_events(req, res):
        @res.event_stream
        async def generate_events():
            yield server_event(*args, **kwargs)

    r = api.client.get("/events", stream=True)
    assert r.status_code == 200
    stream = r.iter_lines()

    received = [next(stream).decode() for _ in lines]
    assert received == lines

    with pytest.raises(StopIteration):
        next(stream)


def test_sse_headers_are_set(api: API):
    @api.route("/events")
    async def view_with_events(req, res):
        @res.event_stream
        async def generate_events():
            yield server_event(name="foo")

    r = api.client.get("/events")
    assert r.status_code == 200
    assert r.headers["connection"] == "keep-alive"
    assert r.headers["content-type"] == "text/event-stream"
    assert r.headers["cache-control"] == "no-cache"


def test_cache_control_header_not_replaced_if_manually_set(api: API):
    @api.route("/events")
    async def sse(req, res):
        @res.event_stream
        async def generate_events():
            yield server_event("hello")

        res.headers["cache-control"] = "foo"

    r = api.client.get("/events")
    assert r.status_code == 200
    assert r.headers["cache-control"] == "foo"


def test_stop_on_client_disconnect(api: API, server):
    num_sent = Value("i", 0)  # Shared accross processes

    @api.route("/events")
    async def sse(req, res):
        @res.event_stream
        async def events():
            nonlocal num_sent
            while True:
                yield server_event("hello")
                num_sent.value += 1

    server.start()
    r = requests.get("http://localhost:8000/events", stream=True)
    assert r.status_code == 200
    assert stops_incrementing(counter=num_sent, response=r, tolerance=5)
