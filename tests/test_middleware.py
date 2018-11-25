from contextlib import contextmanager

from bocadillo import API
from bocadillo.middleware import RoutingMiddleware


@contextmanager
def build_middleware(expect_before=True, expect_after=True, expect_kwargs=None):
    called = {'before': False, 'after': False}
    kwargs = None

    class SetCalled(RoutingMiddleware):
        def __init__(self, app, **kw):
            nonlocal kwargs
            super().__init__(app)
            kwargs = kw

        def before_dispatch(self, req):
            nonlocal called
            called['before'] = True

        def after_dispatch(self, req, res):
            nonlocal called
            called['after'] = True

    yield SetCalled

    assert called['before'] is expect_before
    assert called['after'] is expect_after
    if expect_kwargs is not None:
        assert kwargs == expect_kwargs


def test_if_routing_middleware_is_added_then_it_is_called(api: API):
    with build_middleware() as middleware:
        api.add_middleware(middleware)

        @api.route('/')
        async def index(req, res):
            pass

        api.client.get('/')


def test_can_pass_extra_kwargs(api: API):
    kwargs = {'foo': 'bar'}
    with build_middleware(expect_kwargs=kwargs) as middleware:
        api.add_middleware(middleware, **kwargs)

        @api.route('/')
        async def index(req, res):
            pass

        api.client.get('/')


def test_callbacks_not_called_if_method_not_allowed(api: API):
    with build_middleware(
        expect_before=False, expect_after=False
    ) as middleware:
        api.add_middleware(middleware)

        @api.route('/', methods=['get'])
        async def index(req, res):
            pass

        response = api.client.put('/')
        assert response.status_code == 405
