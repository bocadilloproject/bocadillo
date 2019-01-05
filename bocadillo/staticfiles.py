from os.path import exists

from whitenoise import WhiteNoise

from .compat import WSGIApp, empty_wsgi_app


def static(directory: str) -> WSGIApp:
    """Return a WSGI app that serves static files under the given directory.

    Powered by WhiteNoise.

    # Parameters
    directory (str):
        the path to a directory from where static files should be served.
        If the directory does not exist, no files will be served.

    # Returns
    app (WSGIApp): a WSGI-compliant application.

    # See Also
    - [WhiteNoise](http://whitenoise.evans.io)
    - [WSGI](https://wsgi.readthedocs.io)
    """
    app = WhiteNoise(empty_wsgi_app())
    if exists(directory):
        app.add_files(directory)
    return app
