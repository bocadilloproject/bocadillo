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


class Middleware:
    """Helper for defining Bocadillo middleware."""

    def __init__(self, app):
        self.app = app

    def __call__(self, scope: dict):
        raise NotImplementedError


class BaseMiddleware(Middleware):
    """Base middleware upon which other middleware apps can be added."""

    def add(self, middleware_cls, **kwargs):
        self.app = middleware_cls(self.app, **kwargs)

    def __call__(self, scope: dict):
        return self.app(scope)
