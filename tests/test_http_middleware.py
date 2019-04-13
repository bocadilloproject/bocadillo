from asyncio import sleep
from contextlib import contextmanager

import pytest

from bocadillo import App, ExpectedAsync, HTTPError, Middleware


def test_async_check(app):
    with pytest.raises(ExpectedAsync):

        class BeforeMiddleware(Middleware):
            def before_dispatch(self):
                pass

    with pytest.raises(ExpectedAsync):

        class AfterMiddleware(Middleware):
            def after_dispatch(self):
                pass


@contextmanager
def build_middleware(
    expect_kwargs=None, expect_call_after=True, old_style=False
):
    called = {"before": False, "after": False}
    kwargs = None

    class SetCalled(Middleware):
        if old_style:

            def __init__(self, inner, app: App, **kw):
                super().__init__(inner, app, **kw)
                nonlocal kwargs
                kwargs = kw
                assert isinstance(app, App)

        else:

            def __init__(self, inner, **kw):
                super().__init__(inner, **kw)
                nonlocal kwargs
                kwargs = kw

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
        kwargs.pop("app", None)  # old-style compatibility
        assert kwargs == expect_kwargs


def test_if_middleware_is_added_then_it_is_called(app: App, client):
    with build_middleware() as middleware:
        app.add_middleware(middleware)

        @app.route("/")
        async def index(req, res):
            pass

        client.get("/")


def test_old_style_middleware(app: App, client):
    with build_middleware(old_style=True) as middleware:
        app.add_middleware(middleware)

        @app.route("/")
        async def index(req, res):
            pass

        client.get("/")


def test_can_pass_extra_kwargs(app: App, client):
    kwargs = {"foo": "bar"}
    with build_middleware(expect_kwargs=kwargs) as middleware:
        app.add_middleware(middleware, **kwargs)

        @app.route("/")
        async def index(req, res):
            pass

        client.get("/")


def test_only_before_dispatch_is_called_if_method_not_allowed(app: App, client):
    with build_middleware(expect_call_after=False) as middleware:
        app.add_middleware(middleware)

        @app.route("/")
        async def index(req, res):
            pass

        response = client.put("/")
        assert response.status_code == 405


@pytest.mark.parametrize("when", ["before", "after"])
def test_errors_raised_in_callback_are_handled(app: App, client, when):
    class CustomError(Exception):
        pass

    @app.error_handler(CustomError)
    async def handle_error(req, res, exception):
        res.text = "gotcha!"

    class MiddlewareWithErrors(Middleware):
        async def before_dispatch(self, req, res):
            if when == "before":
                raise CustomError

        async def after_dispatch(self, req, res):
            if when == "after":
                raise CustomError

    app.add_middleware(MiddlewareWithErrors)

    @app.route("/")
    async def index(req, res):
        pass

    r = client.get("/")
    assert r.status_code == 200
    assert r.text == "gotcha!"


def test_middleware_uses_registered_http_error_handler(app: App, client):
    @app.error_handler(HTTPError)
    async def custom(req, res, exc: HTTPError):
        res.status_code = exc.status_code
        res.text = "Foo"

    class NopeMiddleware(Middleware):
        async def before_dispatch(self, req, res):
            raise HTTPError(401)

    app.add_middleware(NopeMiddleware)

    @app.route("/")
    async def index(req, res):
        pass

    response = client.get("/")
    assert response.status_code == 401
    assert response.text == "Foo"


def test_return_response_in_before_hook(app: App, client):
    class NopeMiddleware(Middleware):
        async def before_dispatch(self, req, res):
            res.text = "Foo"
            return res

    app.add_middleware(NopeMiddleware)

    @app.route("/")
    async def index(req, res):
        # Should not be called
        assert False

    r = client.get("/")
    assert r.status_code == 200
    assert r.text == "Foo"


@pytest.mark.xfail(reason="not supported")
def test_middleware_called_if_routed_to_sub_app(app: App, client):
    with build_middleware() as middleware:
        app.add_middleware(middleware)

        sub = App()

        @sub.route("/home")
        async def home(req, res):
            res.text = "OK"

        app.mount("/sub", sub)

        r = client.get("/sub/home")
        assert r.status_code == 200
        assert r.text == "OK"
