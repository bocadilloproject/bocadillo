import bocadillo
from bocadillo.exceptions import HTTPError
from bocadillo.response import Response

api = bocadillo.API(static_root='assets')


# @api.error_handler(HTTPError)
def handle(req, res: Response, exception: HTTPError):
    res.status_code = exception.status_code
    res.text = f'GOTCHA! Overridden {exception.status_code}'


@api.route('/greet/{person}', methods=['post'])
def greet(req, res: Response, person: str):
    res.text = f'Hello, {person}!'


@api.route('/fail/{status:d}')
def fail(req, res, status: int):
    raise HTTPError(status=status)


@api.route('/negation/{x:d}')
def negate(req, res, x: int):
    res.media = {'result': -x}


@api.route('/no-content')
def no_content(req, res):
    res.status_code = 204


@api.route('/add/{x:d}/{y:d}')
class AddView:
    async def get(self, req, res, x: int, y: int):
        res.media = {'result': x + y}


@api.route('/about/{who}', name='about')
async def about(req, res, who):
    res.html = await api.template('about.html', who=who)


@api.route('/google')
async def google(req, res):
    api.redirect(url='https://www.google.com')


@api.route('/home', name='home')
async def home(req, res):
    res.html = await api.template('index.html', app='Bocadillo')


@api.route('/')
async def index(req, res):
    api.redirect(name='home', permanent=True)


if __name__ == '__main__':
    api.run(debug=True)
