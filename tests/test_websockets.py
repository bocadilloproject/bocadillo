from contextlib import suppress

import pytest

from bocadillo import WebSocket, API, WebSocketDisconnect
from bocadillo.constants import WEBSOCKET_CLOSE_CODES


# Basic usage


def test_websocket_route(api: API):
    @api.websocket_route("/chat")
    async def chat(ws: WebSocket):
        async with ws:
            assert await ws.receive_text() == "ping"
            await ws.send_text("pong")

    with api.client.websocket_connect("/chat") as client:
        client.send_text("ping")
        assert client.receive_text() == "pong"


def test_non_existing_endpoint_returns_403_as_per_the_asgi_spec(api: API):
    with pytest.raises(WebSocketDisconnect) as ctx:
        with api.client.websocket_connect("/foo"):
            pass
    assert ctx.value.code == 403


def test_reject_closes_with_403(api: API):
    @api.websocket_route("/foo")
    async def foo(ws: WebSocket):
        await ws.reject()

    with pytest.raises(WebSocketDisconnect) as ctx:
        with api.client.websocket_connect("/foo"):
            pass

    assert ctx.value.code == 403


def test_iter_websocket(api: API):
    @api.websocket_route("/chat")
    async def chat(ws: WebSocket):
        async with ws:
            async for message in ws:
                await ws.send_text(f"You said: {message}")

    with api.client.websocket_connect("/chat") as ws_client:
        ws_client.send_text("ping")
        assert ws_client.receive_text() == "You said: ping"
        ws_client.send_text("pong")
        assert ws_client.receive_text() == "You said: pong"


def test_can_close_within_context(api: API):
    @api.websocket_route("/test")
    async def test(ws: WebSocket):
        async with ws:
            await ws.close(4242)

    with api.client.websocket_connect("/test") as client:
        message = client.receive()

    assert message == {"type": "websocket.close", "code": 4242}


# Encoding / decoding of messages


@pytest.mark.parametrize(
    "receive_type, example_message, expected_type",
    [
        ("bytes", b"Hello", bytes),
        ("text", "Hello", str),
        ("json", {"message": "Hello"}, dict),
    ],
)
def test_receive_type(api: API, receive_type, example_message, expected_type):
    @api.websocket_route("/chat", receive_type=receive_type)
    async def chat(ws: WebSocket):
        async with ws:
            message = await ws.receive()
            assert type(message) == expected_type

    with api.client.websocket_connect("/chat") as client:
        getattr(client, f"send_{receive_type}")(example_message)


@pytest.mark.parametrize(
    "send_type, example_message, expected_type",
    [
        ("bytes", b"Hello", bytes),
        ("text", "Hello", str),
        ("json", {"message": "Hello"}, dict),
    ],
)
def test_send_type(api: API, send_type, example_message, expected_type):
    @api.websocket_route("/chat", send_type=send_type)
    async def chat(ws: WebSocket):
        async with ws:
            await ws.send(example_message)

    with api.client.websocket_connect("/chat") as client:
        message = getattr(client, f"receive_{send_type}")()
        assert type(message) == expected_type
        assert message == example_message


@pytest.mark.parametrize(
    "value_type, example_message, expected_type",
    [
        ("bytes", b"Hello", bytes),
        ("text", "Hello", str),
        ("json", {"message": "Hello"}, dict),
    ],
)
def test_value_type(api: API, value_type, example_message, expected_type):
    @api.websocket_route("/chat", value_type=value_type)
    async def chat(ws: WebSocket):
        async with ws:
            message = await ws.receive()
            assert type(message) == expected_type
            await ws.send(example_message)

    with api.client.websocket_connect("/chat") as client:
        getattr(client, f"send_{value_type}")(example_message)
        assert type(getattr(client, f"receive_{value_type}")()) == expected_type


def test_receive_and_send_event(api: API):
    @api.websocket_route("/chat", value_type="event")
    async def chat(ws: WebSocket):
        async with ws:
            message = await ws.receive()
            assert message == {"type": "websocket.receive", "text": "ping"}
            await ws.send({"type": "websocket.send", "text": "pong"})

    with api.client.websocket_connect("/chat") as client:
        client.send_text("ping")
        assert client.receive_text() == "pong"


# Disconnect errors


@pytest.mark.parametrize(
    "close_codes, code, expected_caught",
    [
        (None, 1000, True),
        (None, 1001, True),
        *(
            (None, code, False)
            for code in WEBSOCKET_CLOSE_CODES
            if code not in (1000, 1001)
        ),
        ((1000,), 1001, False),
        ((1000,), 1000, True),
        *(((), code, False) for code in WEBSOCKET_CLOSE_CODES),
        *((all, code, True) for code in WEBSOCKET_CLOSE_CODES),
    ],
)
def test_catch_disconnect(api: API, close_codes, code, expected_caught):
    caught = False

    @api.websocket_route("/chat", caught_close_codes=close_codes)
    async def chat(ws: WebSocket):
        nonlocal caught
        try:
            async with ws:
                await ws.receive()  # will never receive
            caught = True
        except WebSocketDisconnect as exc:
            # The exception should have been raised only if we told the
            # WebSocket route not to catch it.
            assert exc.code not in ws.caught_close_codes

    with api.client.websocket_connect("/chat") as client:
        # Close immediately.
        client.close(code)

    assert caught is expected_caught


# Server error handling


class Oops(Exception):
    pass


def test_if_exception_raised_in_context_then_closed_with_1011(api: API):
    @api.websocket_route("/fail")
    async def fail(ws: WebSocket):
        async with ws:
            raise Oops

    with suppress(Oops):
        with api.client.websocket_connect("/fail") as client:
            message = client.receive()

    assert message == {"type": "websocket.close", "code": 1011}


def test_accepted_and_exception_raised_then_closed_with_1011(api: API):
    @api.websocket_route("/fail")
    async def fail(ws: WebSocket):
        await ws.accept()
        raise Oops

    with suppress(Oops):
        with api.client.websocket_connect("/fail") as client:
            message = client.receive()

    assert message == {"type": "websocket.close", "code": 1011}


def test_if_not_accepted_and_exception_raised_then_closed_with_1011(api: API):
    @api.websocket_route("/fail")
    async def fail(_):
        raise Oops

    with pytest.raises(WebSocketDisconnect) as ctx:
        with api.client.websocket_connect("/fail"):
            pass

    assert ctx.value.code == 1011
