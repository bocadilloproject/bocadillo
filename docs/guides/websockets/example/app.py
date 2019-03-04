# app.py
from bocadillo import App

app = App()

clients = set()
history = []


@app.websocket_route("/chat", value_type="json")
async def chat(ws):
    async with ws:
        # Register new client
        print("New client:", ws)
        clients.add(ws)

        # Send history of messages
        for message in history:
            await ws.send(message)

        try:
            # Broadcast new messages to all connected clients
            async for message in ws:
                print("Received:", message)
                history.append(message)
                if message["type"] == "message":
                    for client in clients:
                        await client.send(message)
        finally:
            # Make sure we unregister the client in case of unexpected errors.
            # For example, Safari seems to improperly close WebSockets when
            # leaving the page, returning a 1006 close code instead of 1001.
            print("Disconnected:", ws)
            clients.remove(ws)


@app.route("/")
async def index(req, res):
    res.html = await app.template("index.html")


if __name__ == "__main__":
    app.run()
