from contextlib import contextmanager, suppress
from typing import Any, Optional, Union, cast

from .routing import RoutingMixin

try:
    from jinja2 import Environment, FileSystemLoader, Template
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "`jinja2` is not installed. "
        "Have you installed Bocadillo using `bocadillo[templates]`?"
    ) from exc


DEFAULT_TEMPLATES_DIR = "templates"


class Templates:
    """This class provides templating capabilities.

    This is a light wrapper around [jinja2](http://jinja.pocoo.org/docs) and using it requires to install Bocadillo using the `[templates]` extra.

    See also [Templates](../guides/agnostic/templates.md) for detail.

    [RoutingMixin]: ./routing.md#routingmixin

    # Parameters

    ::: tip
    These parameters are also stored as attributes and can be accessed or
    modified at runtime.
    :::

    app (any):
        an optional application object. May be a subclass of [RoutingMixin].
    directory (str):
        The directory where templates should be searched for.
        Passed to the `engine`.
        Defaults to `"templates"` relative to the current working directory.
    context (dict, optional):
        Global template variables passed to the `engine`.
        If present, the app's `.url_for()` method is registered as
        an `url_for` global variable.
    """

    def __init__(
        self,
        app: Optional[Any] = None,
        directory: str = DEFAULT_TEMPLATES_DIR,
        context: dict = None,
    ):
        if context is None:
            context = {}

        with suppress(AttributeError):
            context["url_for"] = app.url_for  # type: ignore

        self.app = app

        self._directory = directory
        self._environment = Environment(
            loader=FileSystemLoader([self.directory]), autoescape=True
        )
        self._environment.globals.update(context)

    @property
    def directory(self) -> str:
        return self._directory

    @directory.setter
    def directory(self, directory: str):
        self._directory = directory
        self._loader.searchpath = [self._directory]  # type: ignore

    @property
    def context(self) -> dict:
        return self._environment.globals

    @context.setter
    def context(self, context: dict):
        self._environment.globals = context

    @property
    def _loader(self) -> FileSystemLoader:
        return cast(FileSystemLoader, self._environment.loader)

    def _get_template(self, name: str) -> Template:
        return self._environment.get_template(name)

    @contextmanager
    def _enable_async(self):
        # Temporarily enable jinja2 async support.
        self._environment.is_async = True
        try:
            yield
        finally:
            self._environment.is_async = False

    async def render(self, filename: str, *args: dict, **kwargs: str) -> str:
        """Render a template asynchronously.

        Can only be used within ``async`` functions.

        # Parameters
        name (str):
            Name of the template, located inside `templates_dir`.
            The trailing underscore avoids collisions with a potential
            context variable named `name`.
        *args (dict):
            Context variables to inject in the template.
        *kwargs (str):
            Context variables to inject in the template.
        """
        with self._enable_async():
            return await self._get_template(filename).render_async(
                *args, **kwargs
            )

    def render_sync(self, filename: str, *args: dict, **kwargs: str) -> str:
        """Render a template synchronously.

        # See Also
        [Templates.render](#render) for the accepted arguments.
        """
        return self._get_template(filename).render(*args, **kwargs)

    def render_string(self, source: str, *args: dict, **kwargs: str) -> str:
        """Render a template from a string (synchronously).

        # Parameters
        source (str): a template given as a string.

        # See Also
        [Templates.render](#render) for the other accepted arguments.
        """
        template = self._environment.from_string(source=source)
        return template.render(*args, **kwargs)
