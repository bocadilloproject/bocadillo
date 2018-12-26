import bocadillo

api = bocadillo.API()


@api.route("/")
class Index:
    async def get(self, req, res):
        res.text = "Hello, world!"


if __name__ == "__main__":
    api.run()
