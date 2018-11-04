import bocadillo
from bocadillo.response import Response

api = bocadillo.API()


@api.route('/greet/{person}')
def greet(req, resp: Response, person: str):
    resp.content = f'Hello, {person}!'


@api.route('/add/{x:d}/{y:d}')
class AddView:

    async def get(self, req, resp, x: int, y: int):
        resp.media = {'result': x + y}


if __name__ == '__main__':
    api.run(debug=True)
