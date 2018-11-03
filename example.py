import bocadillo
from bocadillo.response import Response

api = bocadillo.API()


@api.route('/{greeting}')
async def index(req, resp: Response, greeting):
    resp.media = {'message': f'Hello, {greeting}!'}


if __name__ == '__main__':
    api.run(port=5050, debug=True)
