from bocadillo import API
from bocadillo.exceptions import HTTPError


def test_can_use_simple_function(api: API):
    def validate_has_my_header(req, res, view, params):
        if 'x-my-header' not in req.headers:
            raise HTTPError(400)

    @api.before(validate_has_my_header)
    @api.route('/foo')
    async def foo(req, res):
        res.media = {'header': res.headers['x-my-header']}

    response = api.client.get('/foo')
    assert response.status_code == 400


def test_can_pass_extra_args(api: API):
    def validate_has_my_header(req, res, view, params, header):
        if header not in req.headers:
            raise HTTPError(400)

    @api.before(validate_has_my_header, 'x-my-header')
    @api.route('/foo')
    async def foo(req, res):
        res.media = {'header': res.headers['x-my-header']}

    response = api.client.get('/foo')
    assert response.status_code == 400
