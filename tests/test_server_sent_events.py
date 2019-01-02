import pytest

from bocadillo import API, server_event
from .utils import Oops


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
def test_send_server_events(api: API, args: list, kwargs: dict, lines: list):
    @api.route("/events")
    async def view_with_events(req, res):
        @res.event_stream
        async def generate_events():
            yield server_event(*args, **kwargs)

    r = api.client.get("/events", stream=True)
    assert r.status_code == 200
    assert r.headers["connection"] == "keep-alive"
    assert r.headers["content-type"] == "text/event-stream"
    assert r.headers["cache-control"] == "no-cache"
    assert list(map(bytes.decode, r.iter_lines())) == lines


def test_cache_control_is_not_replaced(api: API):
    @api.route("/events")
    async def sse(req, res):
        @res.event_stream
        async def generate_events():
            yield server_event("hello")

        res.headers["cache-control"] = "foo"

    r = api.client.get("/events")
    assert r.status_code == 200
    assert r.headers["cache-control"] == "foo"
