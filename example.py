import bocadillo
from bocadillo.response import Response

api = bocadillo.API()


@api.route('/{person}')
async def index(req, resp: Response, person: str):
    resp.media = {'message': f'Hello, {person}!'}


if __name__ == '__main__':
    api.run(port=5050, debug=True)
