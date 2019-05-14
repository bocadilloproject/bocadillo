from asyncio import Queue

from bocadillo import App, Templates, server_event

app = App()
templates = Templates()

clients = set()


@app.route("/events")
class Events:
    async def get(self, req, res):
        client = Queue()
        clients.add(client)
        print("New client:", id(client))

        @res.event_stream
        async def send_events():
            hello = {"message": "hello"}
            yield server_event(json=hello, name="hello")
            try:
                while True:
                    message = client.get_nowait()
                    yield server_event(json=message, name="message")
                    print("Sent", message, "to client", id(client))
                    client.task_done()
            finally:
                print("Client disconnected:", id(client))

    async def post(self, req, res):
        json = await req.json()
        for client in clients:
            await client.put(json)
        res.status_code = 201


@app.route("/")
async def index(req, res):
    res.html = await templates.render("index.html")
