from os.path import exists

from whitenoise import WhiteNoise

from .types import WSGIApp
from .wsgi import empty_wsgi_app


def static(directory: str) -> WSGIApp:
    """Return a WSGI app that serves static files under the given directory.

    Powered by WhiteNoise.
    """
    app = WhiteNoise(empty_wsgi_app())
    if exists(directory):
        app.add_files(directory)
    return app
