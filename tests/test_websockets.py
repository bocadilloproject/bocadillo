from bocadillo import WebSocket, API


def test_websocket_route(api: API):
    @api.websocket_route("/chat")
    async def chat(ws: WebSocket):
        async with ws:
            assert await ws.receive_text() == "ping"
            await ws.send_text("pong")

    with api.client.websocket_connect("/chat") as ws_client:
        ws_client.send_text("ping")
        assert ws_client.receive_text() == "pong"
