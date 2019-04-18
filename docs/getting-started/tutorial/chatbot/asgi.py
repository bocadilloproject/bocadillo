"""ASGI server entry point."""
from bocadillo import configure
from .app import app
from . import settings

configure(app, settings)
