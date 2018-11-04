import bocadillo
from bocadillo.response import Response

api = bocadillo.API()


@api.route('/add/{x:d}/{y:d}')
class AddView:

    def get(self, req, resp, x: int, y: int):
        resp.media = {'result': x + y}


@api.route('/greet/{person}')
def index(req, resp: Response, person: str):
    resp.media = {'message': f'Hello, {person}!'}


if __name__ == '__main__':
    api.run(debug=True)
