import bocadillo
from bocadillo.exceptions import HTTPError
from bocadillo.response import Response

api = bocadillo.API(static_root='assets')


@api.error_handler(HTTPError)
def handle(req, resp: Response, exception: HTTPError):
    resp.status_code = exception.status_code
    resp.text = f'GOTCHA! Overridden {exception.status_code}'


@api.route('/greet/{person}', methods=['post'])
def greet(req, resp: Response, person: str):
    resp.text = f'Hello, {person}!'


@api.route('/fail/{status:d}')
def fail(req, resp, status: int):
    raise HTTPError(status=status)


@api.route('/negation/{x:d}')
def negate(req, res, x: int):
    res.media = {'result': -x}


@api.route('/add/{x:d}/{y:d}')
class AddView:

    async def get(self, req, resp, x: int, y: int):
        resp.media = {'result': x + y}


@api.route('/')
async def index(req, resp):
    resp.html = await api.template('index.html', app='Bocadillo')


if __name__ == '__main__':
    api.run(debug=True)
