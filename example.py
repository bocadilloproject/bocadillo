import bocadillo
from bocadillo.http_error import HTTPError
from bocadillo.response import Response

api = bocadillo.API()


@api.error_handler(HTTPError)
def handle(req, resp: Response, exception: HTTPError):
    resp.status_code = exception.status_code
    resp.content = f'GOTCHA! Overridden {exception.status_code}'


@api.route('/greet/{person}', methods=['post'])
def greet(req, resp: Response, person: str):
    resp.content = f'Hello, {person}!'


@api.route('/fail/{status:d}')
def fail(req, resp, status: int):
    raise HTTPError(status=status)


@api.route('/add/{x:d}/{y:d}')
class AddView:

    async def get(self, req, resp, x: int, y: int):
        resp.media = {'result': x + y}


if __name__ == '__main__':
    api.run(debug=True)
