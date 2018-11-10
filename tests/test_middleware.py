from bocadillo import API
from bocadillo.middleware import Middleware


def test_if_middleware_is_added_then_it_is_called(api: API):
    called = False
    params = {}

    class SetCalled(Middleware):

        def __init__(self, app, **kwargs):
            super().__init__(app)
            self._kwargs = kwargs

        def __call__(self, scope: dict):
            instance = self._app(scope)

            async def asgi(receive, send):
                nonlocal called, params
                called = True
                params = self._kwargs
                await instance(receive, send)

            return asgi

    api.add_middleware(SetCalled, foo='bar')

    @api.route('/')
    async def index(req, res):
        pass

    api.client.get('/')
    assert called
    assert params == {'foo': 'bar'}
