from bocadillo import App

app = App()


@app.route("/")
async def index(req, res):
    res.text = "Hello, world!"
