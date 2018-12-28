import pytest

from bocadillo import WebSocket, API, WebSocketDisconnect


def test_websocket_route(api: API):
    @api.websocket_route("/chat")
    async def chat(ws: WebSocket):
        async with ws:
            assert await ws.receive_text() == "ping"
            await ws.send_text("pong")

    with api.client.websocket_connect("/chat") as ws_client:
        ws_client.send_text("ping")
        assert ws_client.receive_text() == "pong"


def test_non_existing_endpoint_returns_403_as_per_the_asgi_spec(api: API):
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
        assert type(getattr(client, f"receive_{send_type}")()) == expected_type


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


@pytest.mark.parametrize("catch_disconnect", [True, False])
def test_catch_disconnect(api: API, catch_disconnect):
    caught = False

    @api.websocket_route("/chat", catch_disconnect=catch_disconnect)
    async def chat(ws: WebSocket):
        nonlocal caught
        try:
            async with ws:
                await ws.receive()  # will never receive
            caught = True
        except WebSocketDisconnect:
            # The exception should be raised only if we told the WebSocket
            # not to catch it.
            assert not catch_disconnect

    with api.client.websocket_connect("/chat"):
        # Don't send anything, which causes the server to disconnect the client.
        pass

    # The block after the `async with` block must have been called
    # only if it caught the disconnect exception.
    assert caught == catch_disconnect
