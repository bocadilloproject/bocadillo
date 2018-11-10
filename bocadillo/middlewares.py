"""Bocadillo middleware definition.

A middleware is a class that implements the ASGI protocol.
"""
from .request import Request


class AppMiddleware:
    """Middleware for Bocadillo applications."""

    def __init__(self, app):
        self.app = app

    def __call__(self, scope: dict):
        async def asgi(receive, send):
            nonlocal scope
            request = Request(scope, receive)
            response = await self.app.dispatch(request)
            await response(receive, send)

        return asgi


class BaseMiddleware:
    """Base middleware upon which other middleware apps can be added."""

    def __init__(self, app):
        self._app = app

    def add(self, middleware_cls, **kwargs):
        self._app = middleware_cls(self._app, **kwargs)

    def __call__(self, scope: dict):
        return self._app(scope)
