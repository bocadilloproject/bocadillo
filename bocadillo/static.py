from whitenoise import WhiteNoise

from .compat import empty_wsgi_app
from .types import WSGIApp


def static(directory: str) -> WSGIApp:
    app = WhiteNoise(empty_wsgi_app())
    app.add_files(directory)
    return app
