from bocadillo import API, Recipe, WebSocket


def test_websocket_recipe_route(api: API):
    chat = Recipe("chat")

    @chat.websocket_route("/room/{name}", receive_type="json", send_type="text")
    async def chat_room(ws: WebSocket, name: str):
        async with ws:
            message = await ws.receive()
            await ws.send(f"[{name}]: {message['text']}")

    api.recipe(chat)

    with api.client.websocket_connect("/chat/room/test") as client:
        client.send_json({"text": "Hello"})
        assert client.receive_text() == "[test]: Hello"
