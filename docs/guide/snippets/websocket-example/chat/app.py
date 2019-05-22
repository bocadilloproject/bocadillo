# chat/app.py
from bocadillo import App, provider, Templates

app = App()
templates = Templates()


@provider(scope="app")
async def history() -> list:
    return []


@provider(scope="app")
async def clients() -> set:
    return set()


@app.websocket_route("/chat", value_type="json")
async def chat(ws, history, clients):
    # Register new client
    print("New client:", ws)
    clients.add(ws)

    # Send history of messages.
    for message in history:
        await ws.send(message)

    try:
        # Broadcast incoming messages to all connected clients.
        async for message in ws:
            print("Received:", message)
            history.append(message)
            if message["type"] == "message":
                for client in clients:
                    await client.send(message)
    finally:
        print("Disconnected:", ws)
        clients.remove(ws)


@app.route("/")
async def index(req, res):
    res.html = await templates.render("index.html")
