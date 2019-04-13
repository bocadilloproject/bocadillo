from contextlib import suppress

import pytest

from bocadillo import App, ExpectedAsync, WebSocket, WebSocketDisconnect
from bocadillo.constants import WEBSOCKET_CLOSE_CODES

# Basic usage


def test_websocket_route(app: App, client):
    @app.websocket_route("/chat")
    async def chat(ws: WebSocket):
        assert await ws.receive_text() == "ping"
        await ws.send_text("pong")

    with client.websocket_connect("/chat") as ws:
        ws.send_text("ping")
        assert ws.receive_text() == "pong"


def test_async_check(app):
    def chat(ws):
        pass

    with pytest.raises(ExpectedAsync):
        app.websocket_route("/chat")(chat)


def test_enter_context_twice_is_safe(app: App, client):
    # Ensures compatibility with <0.13.1.

    @app.websocket_route("/chat")  # auto_accept==True
    async def chat(ws: WebSocket):
        async with ws:  # <-- should be OK (previous API)
            assert await ws.receive_text() == "ping"
            await ws.send_text("pong")

    with client.websocket_connect("/chat") as ws:
        ws.send_text("ping")
        assert ws.receive_text() == "pong"


def test_manual_accept(app: App, client):
    @app.websocket_route("/chat", auto_accept=False)
    async def chat(ws: WebSocket):
        async with ws:
            assert await ws.receive_text() == "ping"
            await ws.send_text("pong")

    with client.websocket_connect("chat") as ws:
        ws.send_text("ping")
        assert ws.receive_text() == "pong"


def test_websocket_route_parameters(app: App, client):
    @app.websocket_route("/chat/{room}")
    async def chat_room(ws: WebSocket, room: str):
        await ws.send(room)

    with client.websocket_connect("/chat/foo") as ws:
        assert ws.receive_text() == "foo"


def test_non_existing_endpoint_returns_403_as_per_the_asgi_spec(client):
    with pytest.raises(WebSocketDisconnect) as ctx:
        with client.websocket_connect("/foo"):
            pass
    assert ctx.value.code == 403


def test_reject_closes_with_403(app: App, client):
    @app.websocket_route("/foo", auto_accept=False)
    async def foo(ws: WebSocket):
        await ws.reject()

    with pytest.raises(WebSocketDisconnect) as ctx:
        with client.websocket_connect("/foo"):
            pass

    assert ctx.value.code == 403


def test_iter_websocket(app: App, client):
    @app.websocket_route("/chat")
    async def chat(ws: WebSocket):
        async for message in ws:
            await ws.send_text(f"You said: {message}")

    with client.websocket_connect("/chat") as ws:
        ws.send_text("ping")
        assert ws.receive_text() == "You said: ping"
        ws.send_text("pong")
        assert ws.receive_text() == "You said: pong"


@pytest.mark.parametrize("manual", (True, False))
def test_can_close_within_context(app: App, client, manual: bool):
    @app.websocket_route("/test", auto_accept=not manual)
    async def test(ws: WebSocket):
        if manual:
            async with ws:
                await ws.close(4242)
        else:
            await ws.close(4242)

    with client.websocket_connect("/test") as ws:
        message = ws.receive()

    assert message == {"type": "websocket.close", "code": 4242}


def test_websocket_url(app: App, client):
    @app.websocket_route("/test")
    async def test(ws: WebSocket):
        assert ws.url == "ws://testserver/test"
        assert ws.url.path == "/test"
        assert ws.url.port is None
        assert ws.url.scheme == "ws"
        assert ws.url.hostname == "testserver"
        assert ws.url.query == ""
        assert ws.url.is_secure is False

    with client.websocket_connect("/test"):
        pass


def test_websocket_headers(app: App, client):
    @app.websocket_route("/test")
    async def test(ws: WebSocket):
        await ws.send_json(dict(ws.headers))

    with client.websocket_connect("/test", headers={"X-Foo": "bar"}) as ws:
        headers = ws.receive_json()

    assert headers["x-foo"] == "bar"


def test_websocket_query_params(app: App, client):
    @app.websocket_route("/test")
    async def test(ws: WebSocket):
        await ws.send_json(dict(ws.query_params))

    with client.websocket_connect("/test?q=hello") as ws:
        query_params = ws.receive_json()

    assert query_params["q"] == "hello"


# Encoding / decoding of messages


@pytest.mark.parametrize(
    "receive_type, example_message, expected_type",
    [
        ("bytes", b"Hello", bytes),
        ("text", "Hello", str),
        ("json", {"message": "Hello"}, dict),
    ],
)
def test_receive_type(
    app: App, client, receive_type, example_message, expected_type
):
    @app.websocket_route("/chat", receive_type=receive_type)
    async def chat(ws: WebSocket):
        message = await ws.receive()
        assert type(message) == expected_type

    with client.websocket_connect("/chat") as ws:
        getattr(ws, f"send_{receive_type}")(example_message)


@pytest.mark.parametrize(
    "send_type, example_message, expected_type",
    [
        ("bytes", b"Hello", bytes),
        ("text", "Hello", str),
        ("json", {"message": "Hello"}, dict),
    ],
)
def test_send_type(app: App, client, send_type, example_message, expected_type):
    @app.websocket_route("/chat", send_type=send_type)
    async def chat(ws: WebSocket):
        await ws.send(example_message)

    with client.websocket_connect("/chat") as ws:
        message = getattr(ws, f"receive_{send_type}")()
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
def test_value_type(
    app: App, client, value_type, example_message, expected_type
):
    @app.websocket_route("/chat", value_type=value_type)
    async def chat(ws: WebSocket):
        message = await ws.receive()
        assert type(message) == expected_type
        await ws.send(example_message)

    with client.websocket_connect("/chat") as ws:
        getattr(ws, f"send_{value_type}")(example_message)
        assert type(getattr(ws, f"receive_{value_type}")()) == expected_type


def test_receive_and_send_event(app: App, client):
    @app.websocket_route("/chat", value_type="event")
    async def chat(ws: WebSocket):
        message = await ws.receive()
        assert message == {"type": "websocket.receive", "text": "ping"}
        await ws.send({"type": "websocket.send", "text": "pong"})

    with client.websocket_connect("/chat") as ws:
        ws.send_text("ping")
        assert ws.receive_text() == "pong"


# Disconnect errors


@pytest.mark.parametrize(
    "close_codes, code, expected_caught",
    [
        *((None, code, True) for code in (1000, 1001)),
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
def test_catch_disconnect(app: App, client, close_codes, code, expected_caught):
    caught = False

    @app.websocket_route(
        "/chat", auto_accept=False, caught_close_codes=close_codes
    )
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

    with client.websocket_connect("/chat") as ws:
        # Close immediately.
        ws.close(code)

    assert caught is expected_caught


# Server error handling


class Oops(Exception):
    pass


def test_if_exception_raised_in_context_then_closed_with_1011(app: App, client):
    @app.websocket_route("/fail")
    async def fail(ws: WebSocket):
        raise Oops

    with suppress(Oops):
        with client.websocket_connect("/fail") as ws:
            message = ws.receive()

    assert message == {"type": "websocket.close", "code": 1011}


def test_accepted_and_exception_raised_then_closed_with_1011(app: App, client):
    @app.websocket_route("/fail", auto_accept=False)
    async def fail(ws: WebSocket):
        await ws.accept()
        raise Oops

    with suppress(Oops):
        with client.websocket_connect("/fail") as ws:
            message = ws.receive()

    assert message == {"type": "websocket.close", "code": 1011}


def test_if_not_accepted_and_exception_raised_then_closed_with_1011(
    app: App, client
):
    @app.websocket_route("/fail", auto_accept=False)
    async def fail(_):
        raise Oops

    with pytest.raises(WebSocketDisconnect) as ctx:
        with client.websocket_connect("/fail"):
            pass

    assert ctx.value.code == 1011


def test_context_does_not_silence_exceptions(app: App, client):
    cleaned_up = False

    @app.websocket_route("/fail", auto_accept=False)
    async def fail(ws):
        nonlocal cleaned_up
        async with ws:
            raise Oops
        cleaned_up = True

    with suppress(Oops):
        with client.websocket_connect("/fail"):
            pass

    assert not cleaned_up
