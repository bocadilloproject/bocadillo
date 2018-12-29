from bocadillo import API

api = API()

clients = set()
messages = []


@api.websocket_route("/chat", value_type="json")
async def chat(ws):
    async with ws:
        print("New client:", ws)
        clients.add(ws)
        for message in messages:
            await ws.send(message)

        async for message in ws:
            print(message)
            messages.append(message)
            if message["type"] == "message":
                for client in clients:
                    await client.send(message)

    clients.remove(ws)


@api.route("/")
async def index(req, res):
    res.html = await api.template("index.html")


if __name__ == "__main__":
    api.run()
