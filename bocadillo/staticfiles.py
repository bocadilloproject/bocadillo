from os.path import exists

from whitenoise import WhiteNoise

from .compat import WSGIApp, empty_wsgi_app


def static(root: str, **kwargs) -> WSGIApp:
    """Return a WSGI app that serves static files under the given directory.

    Powered by [WhiteNoise](http://whitenoise.evans.io).

    [config-attrs]: http://whitenoise.evans.io/en/stable/base.html#configuration-attributes

    # Parameters
    root (str):
        the path to a directory from where static files should be served.
        If the directory does not exist, no files will be served.
    **kwargs (any):
        keyword arguments passed to the WhiteNoise constructor. See also [Configuration attributes (WhiteNoise docs)][config-attrs].

    # Returns
    app (callable): a WhiteNoise WSGI app.
    """
    if exists(root):
        kwargs["root"] = root
    return WhiteNoise(empty_wsgi_app(), **kwargs)
