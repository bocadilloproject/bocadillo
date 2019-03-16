from datetime import datetime
from asyncio import sleep
from bocadillo import App, server_event

app = App()


@app.route("/clock")
async def clock(req, res):
    @res.event_stream
    async def stream():
        while True:
            millis = datetime.now().timestamp() * 1000
            yield server_event(data=str(millis))
            await sleep(1)


@app.route("/")
async def index(req, res):
    res.html = """
        <html>
        <head><meta charset="utf-8"/></head>
        <body>
            <h1>⏱ SSE-powered Clock</h1>
            <div id="time"></div>
            <script>
                const counter = new EventSource("/clock");
                const time = document.getElementById("time");
                counter.onmessage = (e) => {
                    time.innerText = new Date(+e.data).toString();
                };
            </script>
        </body>
    </html>
    """


if __name__ == "__main__":
    app.run()
