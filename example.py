import bocadillo
from bocadillo.response import Response

api = bocadillo.API()


@api.error_handler(KeyError)
def handle(req, resp, exception):
    resp.content = 'GOTCHA!'


@api.route('/greet/{person}')
def greet(req, resp: Response, person: str):
    resp.content = f'Hello, {person}!'


@api.route('/fail')
def fail(req, resp):
    raise KeyError('GOTCHA!')


@api.route('/add/{x:d}/{y:d}')
class AddView:

    async def get(self, req, resp, x: int, y: int):
        resp.media = {'result': x + y}


if __name__ == '__main__':
    api.run(debug=True)
