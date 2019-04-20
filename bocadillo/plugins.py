import os
import typing

import typesystem
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .config import SettingsError, settings
from .constants import DEFAULT_CORS_CONFIG
from .converters import PathConversionError
from .error_handlers import error_to_json
from .errors import HTTPError
from .staticfiles import static
from .injection import STORE

if typing.TYPE_CHECKING:
    from .applications import App

PluginFunction = typing.Callable[["App"], None]

_PLUGINS: typing.Dict[str, PluginFunction] = {}


def plugin(func: PluginFunction):
    """Register a new plugin."""
    _PLUGINS[func.__name__] = func
    return func


def get_plugins() -> typing.Dict[str, PluginFunction]:
    """Return the currently registered plugins."""
    return _PLUGINS


@plugin
def use_providers(app: "App"):
    """Configure providers.

    This plugin is always enabled. It ensures that app-scoped providers
    are correctly setup on app startup, and tore down on app shutdown, and
    resolves dependencies between providers.
    """
    STORE.freeze()
    app.on("startup", STORE.enter_session)
    app.on("shutdown", STORE.exit_session)


@plugin
def use_allowed_hosts(app: "App"):
    """Restrict which hosts an application is allowed to be served at.

    Settings:
    - `ALLOWED_HOSTS` (list of str, optional):
        a list of hosts. If the list contains `"*"`, any host is allowed.
        Defaults to `["*"]`.
    """
    allowed_hosts = settings.get("ALLOWED_HOSTS")
    if allowed_hosts is None:
        allowed_hosts = ["*"]

    app.add_asgi_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)


@plugin
def use_cors(app: "App"):
    """Enable CORS (Cross-Origin Resource Sharing) headers.

    [constants.py]: /api/constants.md
    [CORSMiddleware]: https://www.starlette.io/middleware/#corsmiddleware

    Settings:
    - `CORS` (bool or dict):
        if `True`, the default configuration defined in [constants.py] is used.
        Otherwise, the dictionary is passed to Starlette's [CORSMiddleware].
    """
    cors: typing.Optional[typing.Union[bool, dict]] = settings.get("CORS")

    if cors is None:
        return

    if cors is True:
        cors = dict(DEFAULT_CORS_CONFIG)

    app.add_asgi_middleware(CORSMiddleware, **cors)


@plugin
def use_gzip(app: "App"):
    """Enable [GZip] compression.

    [GZip]: /guides/http/middleware.md#gzip

    Settings:
    - `GZIP` (bool):
        if `True`, automatically compress responses for clients that support it.
        Defaults to `False`.
    - `GZIP_MIN_SIZE` (int):
        compress only responses that have more bytes than the specified value.
        Defaults to `1024`.
    """
    if not settings.get("GZIP", False):
        return

    gzip_min_size = settings.get("GZIP_MIN_SIZE", 1024)
    app.add_asgi_middleware(GZipMiddleware, minimum_size=gzip_min_size)


@plugin
def use_hsts(app: "App"):
    """Enable [HSTS].

    [HSTS]: /guides/http/middleware.md#hsts

    Settings:
    - `HSTS` (bool):
        if `True`, HTTP traffic is automatically redirected to HTTPS.
        Defaults to `False`.
    """
    if not settings.get("HSTS"):
        return

    app.add_asgi_middleware(HTTPSRedirectMiddleware)


@plugin
def use_sessions(app: "App"):
    """Enable cookie-based signed sessions.

    [SessionMiddleware]: https://www.starlette.io/middleware/#sessionmiddleware

    Settings:
    - `SESSIONS` (bool or dict):
        if `True`, the secret key is obtained from the `SECRET_KEY` environment
        variable. Otherwise, it must be a dictionary which will be passed
        to Starlette's [SessionMiddleware].
    """
    sessions = settings.get("SESSIONS")

    if sessions is None:
        return

    try:
        from starlette.middleware.sessions import SessionMiddleware
    except ImportError as exc:  # pragma: no cover
        if "itsdangerous" in str(exc):
            raise ImportError(
                "Please install the [sessions] extra to use sessions: "
                "`pip install bocadillo[sessions]`."
            ) from exc
        raise exc from None

    if sessions is True:
        sessions = {"secret_key": os.getenv("SECRET_KEY")}

    if not sessions.get("secret_key"):
        raise SettingsError(
            "`SESSIONS` must have a non-empty `secret_key` to use sessions."
        )

    app.add_asgi_middleware(SessionMiddleware, **sessions)


@plugin
def use_staticfiles(app: "App"):
    """Enable static files serving with WhiteNoise.

    Settings:
    - `STATIC_DIR` (str):
        the name of the directory containing static files, relative to
        the application entry point.
        Set to `None` to not serve any static files.
        Defaults to `"static"`.
    - `STATIC_ROOT` (str):
        the path prefix for static assets. Defaults to `"static"`.
    - `STATIC_CONFIG` (dict):
        extra static files configuration attributes.
        See also #::bocadillo.staticfiles#static.
    """
    static_root = settings.get("STATIC_ROOT", "static")
    static_dir = settings.get("STATIC_DIR", "static")
    static_config = settings.get("STATIC_CONFIG", {})

    if static_dir is None:
        return

    app.mount(static_root, static(static_dir, **static_config))


@plugin
def use_path_conversion_error_handling(app: "App"):
    @app.error_handler(PathConversionError)
    async def on_path_conversion_error(req, res, exc: PathConversionError):
        raise HTTPError(400, detail=dict(exc))


@plugin
def use_typesystem_validation_error_handling(app: "App"):
    """Setup an error handler for `typesystem.ValidationError`.

    This plugin allows to validate TypeSystem schemas while letting the
    framework deal with formatting and sending back a `400 Bad Request`
    error response in case of invalid data.

    Settings:
    - `HANDLE_TYPESYSTEM_VALIDATION_ERRORS` (bool):
        Set to `False` to disable this plugin. Defaults to `True`.
    """
    if not settings.get("HANDLE_TYPESYSTEM_VALIDATION_ERRORS", True):
        return

    @app.error_handler(typesystem.ValidationError)
    async def handle_validation_error(req, res, exc):
        detail = dict(exc)
        # Don't just re-raise `HTTPError` for handling by the configured
        # error handler, because we really want to return JSON.
        await error_to_json(req, res, HTTPError(400, detail=detail))
