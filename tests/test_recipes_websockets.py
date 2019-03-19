from bocadillo import App, Recipe, WebSocket


def test_websocket_recipe_route(app: App, client):
    chat = Recipe("chat")

    @chat.websocket_route("/room/{name}", receive_type="json", send_type="text")
    async def chat_room(ws: WebSocket, name: str):
        message = await ws.receive()
        await ws.send(f"[{name}]: {message['text']}")

    app.recipe(chat)

    with client.websocket_connect("/chat/room/test") as ws:
        ws.send_json({"text": "Hello"})
        assert ws.receive_text() == "[test]: Hello"
