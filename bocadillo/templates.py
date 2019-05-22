import pathlib
import typing
from contextlib import contextmanager

from jinja2 import Environment, FileSystemLoader, Template


class Templates:
    """This class provides templating capabilities.

    This is a light wrapper around [jinja2](http://jinja.pocoo.org/docs).

    See also [Templates](/guide/templates.md) for detail.

    ::: tip
    Parameters are also stored as attributes and can be accessed or
    modified at runtime.
    :::

    # Parameters
    directory (str):
        the directory where templates should be searched for.
        Defaults to `"templates"` relative to the current working directory.
    context (dict, optional):
        global template variables.
    """

    __slots__ = ("_directory", "_environment")

    def __init__(
        self,
        *args,  # compatibility with `Templates(app)`
        directory: typing.Union[str, pathlib.Path] = "templates",
        context: dict = None
    ):
        if context is None:
            context = {}
        self._directory = str(directory)
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
        return typing.cast(FileSystemLoader, self._environment.loader)

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

    async def render(
        self, filename: str, *args: dict, **kwargs: typing.Any
    ) -> str:
        """Render a template asynchronously.

        Can only be used within async functions.

        # Parameters
        name (str):
            name of the template, located inside `templates_dir`.
            The trailing underscore avoids collisions with a potential
            context variable named `name`.
        *args (dict):
            context variables to inject in the template.
        *kwargs (str):
            context variables to inject in the template.
        """
        with self._enable_async():
            return await self._get_template(filename).render_async(
                *args, **kwargs
            )

    def render_sync(
        self, filename: str, *args: dict, **kwargs: typing.Any
    ) -> str:
        """Render a template synchronously.

        # See Also
        [Templates.render](#render) for the accepted arguments.
        """
        return self._get_template(filename).render(*args, **kwargs)

    def render_string(
        self, source: str, *args: dict, **kwargs: typing.Any
    ) -> str:
        """Render a template from a string (synchronously).

        # Parameters
        source (str): a template given as a string.

        # See Also
        [Templates.render](#render) for the other accepted arguments.
        """
        template = self._environment.from_string(source=source)
        return template.render(*args, **kwargs)
