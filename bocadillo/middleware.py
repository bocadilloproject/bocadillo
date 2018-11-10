"""Bocadillo middleware definition.

A middleware is a class that implements the ASGI protocol.

There are two kinds of middleware classes:
- Routing middleware: suited for performing operations before and after
routing occurs.
- Common middleware: suited for all other middleware operations.

Common middleware should be called first, then routing middleware, which should
end up calling the actual Bocadillo API object.
"""
from .request import Request


class Middleware:
    """Base class for middleware classes."""

    def __init__(self, app):
        self.app = app

    def add(self, middleware_cls, **kwargs):
        self.app = middleware_cls(self.app, **kwargs)

    def __call__(self, scope: dict):
        raise NotImplementedError


class CommonMiddleware(Middleware):
    """Base middleware for non-routing operations."""

    def __call__(self, scope: dict):
        return self.app(scope)


class RoutingMiddleware(Middleware):
    """Helper for middleware that act before and after routing."""

    def before_dispatch(self, req):
        pass

    def after_dispatch(self, req, res):
        pass

    async def dispatch(self, request):
        self.before_dispatch(request)
        response = await self.app.dispatch(request)
        self.after_dispatch(request, response)
        return response

    def __call__(self, scope: dict):
        async def asgi(receive, send):
            nonlocal scope
            request = Request(scope, receive)
            response = await self.dispatch(request)
            await response(receive, send)

        return asgi
