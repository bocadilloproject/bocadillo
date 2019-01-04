from asyncio import sleep
from contextlib import contextmanager

import pytest

from bocadillo import API, Middleware, HTTPError


@contextmanager
def build_middleware(expect_kwargs=None, sync=False, expect_call_after=True):
    called = {"before": False, "after": False}
    kwargs = None

    class SetCalled(Middleware):
        def __init__(self, app, **kw):
            nonlocal kwargs
            kwargs = kw
            super().__init__(app, **kw)

        if sync:

            def before_dispatch(self, req, res):
                nonlocal called
                called["before"] = True

            def after_dispatch(self, req, res):
                nonlocal called
                called["after"] = True

        else:

            async def before_dispatch(self, req, res):
                nonlocal called
                await sleep(0.01)
                called["before"] = True

            async def after_dispatch(self, req, res):
                nonlocal called
                await sleep(0.01)
                called["after"] = True

    yield SetCalled

    assert called["before"] is True
    assert called["after"] is expect_call_after
    if expect_kwargs is not None:
        assert kwargs == expect_kwargs


def test_if_middleware_is_added_then_it_is_called(api: API):
    with build_middleware() as middleware:
        api.add_middleware(middleware)

        @api.route("/")
        async def index(req, res):
            pass

        api.client.get("/")


def test_can_pass_extra_kwargs(api: API):
    kwargs = {"foo": "bar"}
    with build_middleware(expect_kwargs=kwargs) as middleware:
        api.add_middleware(middleware, **kwargs)

        @api.route("/")
        async def index(req, res):
            pass

        api.client.get("/")


def test_callbacks_are_called_if_method_not_allowed(api: API):
    with build_middleware(expect_call_after=False) as middleware:
        api.add_middleware(middleware)

        @api.route("/")
        async def index(req, res):
            pass

        response = api.client.put("/")
        assert response.status_code == 405


def test_callbacks_can_be_sync(api: API):
    with build_middleware(sync=True) as middleware:
        api.add_middleware(middleware)

        @api.route("/")
        async def index(req, res):
            pass

        response = api.client.get("/")
        assert response.status_code == 200


@pytest.mark.parametrize("when", ["before", "after"])
def test_errors_raised_in_callback_are_handled(api: API, when):
    class CustomError(Exception):
        pass

    @api.error_handler(CustomError)
    def handle_error(req, res, exception):
        res.text = "gotcha!"

    class MiddlewareWithErrors(Middleware):
        async def before_dispatch(self, req, res):
            if when == "before":
                raise CustomError

        async def after_dispatch(self, req, res):
            if when == "after":
                raise CustomError

    api.add_middleware(MiddlewareWithErrors)

    @api.route("/")
    async def index(req, res):
        pass

    client = api.build_client(raise_server_exceptions=False)
    r = client.get("/")
    assert r.status_code == 200
    assert r.text == "gotcha!"


def test_middleware_uses_registered_http_error_handler(api: API):
    @api.error_handler(HTTPError)
    def custom(req, res, exc: HTTPError):
        res.status_code = exc.status_code
        res.text = "Foo"

    class NopeMiddleware(Middleware):
        async def before_dispatch(self, req, res):
            raise HTTPError(401)

    api.add_middleware(NopeMiddleware)

    @api.route("/")
    async def index(req, res):
        pass

    response = api.client.get("/")
    assert response.status_code == 401
    assert response.text == "Foo"
