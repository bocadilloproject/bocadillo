from bocadillo import API
from bocadillo.middleware import RoutingMiddleware


def test_if_routing_middleware_is_added_then_it_is_called(api: API):
    called = False
    params = {}

    class SetCalled(RoutingMiddleware):

        def __init__(self, app, **kwargs):
            super().__init__(app)
            self._kwargs = kwargs

        def before_dispatch(self, req):
            nonlocal called
            called = True

        def after_dispatch(self, req, res):
            nonlocal params
            params = self._kwargs

    api.add_middleware(SetCalled, foo='bar')

    @api.route('/')
    async def index(req, res):
        pass

    api.client.get('/')
    assert called
    assert params == {'foo': 'bar'}
