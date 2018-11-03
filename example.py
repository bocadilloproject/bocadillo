import bocadillo

api = bocadillo.API()


@api.route('/')
def index(req, resp):
    resp.media = {'message': 'Hello, world!'}


if __name__ == '__main__':
    api.run(port=5050, debug=False)
