import bocadillo

api = bocadillo.API()


@api.route("/")
async def index(req, res):
    res.text = "Hello, world!"


if __name__ == "__main__":
    api.run()
