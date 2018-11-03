import bocadillo

api = bocadillo.API()


@api.route('/')
def index(req, resp):
    resp.media = {'message': 'Hello, world!'}


if __name__ == '__main__':
    api.run(host='localhost', port=5050)
