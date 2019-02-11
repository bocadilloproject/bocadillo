from contextlib import contextmanager
from typing import List, Coroutine, Optional

from jinja2 import Environment, FileSystemLoader
from jinja2 import Template as _Template

Template = _Template

DEFAULT_TEMPLATES_DIR = "templates"


def get_templates_environment(template_dirs: List[str]):
    return Environment(
        loader=FileSystemLoader(template_dirs),
        autoescape=True,
        enable_async=True,
    )


class TemplatesMixin:
    """Provide templating capabilities to an application class."""

    def __init__(self, templates_dir: str = None, **kwargs):
        super().__init__(**kwargs)
        dirs: List[str]
        if templates_dir is None:
            dirs = []
        else:
            dirs = [templates_dir]
        self._templates = get_templates_environment(dirs)
        self._templates.globals.update(self.get_template_globals())

    def get_template_globals(self) -> dict:
        return {}

    @property
    def templates_dir(self) -> Optional[str]:
        """The path where templates are searched for, or `None` if not set.

        This is built from the `templates_dir` parameter.
        """
        loader: FileSystemLoader = self._templates.loader
        try:
            return loader.searchpath[0]
        except IndexError:
            return None

    @templates_dir.setter
    def templates_dir(self, templates_dir: str):
        loader: FileSystemLoader = self._templates.loader
        loader.searchpath = [templates_dir]

    def _get_template(self, name: str) -> Template:
        return self._templates.get_template(name)

    @contextmanager
    def _prevent_async_template_rendering(self):
        """If enabled, temporarily disable async template rendering."""
        # Hot fix for a bug with Jinja2's async environment, which always
        # renders asynchronously even under `render()`.
        # Example error:
        # `RuntimeError: There is no current event loop in thread [...]`
        initial = self._templates.is_async
        self._templates.is_async = False
        try:
            yield
        finally:
            self._templates.is_async = initial

    @staticmethod
    def _prepare_context(context: dict = None, **kwargs):
        if context is None:
            context = {}
        context.update(kwargs)
        return context

    async def template(self, name_: str, context: dict = None, **kwargs) -> str:
        """Render a template asynchronously.

        Can only be used within `async` functions.

        # Parameters

        name (str):
            Name of the template, located inside `templates_dir`.
            The trailing underscore avoids collisions with a potential
            context variable named `name`.
        context (dict):
            Context variables to inject in the template.
        kwargs (dict):
            Context variables to inject in the template.
        """
        context = self._prepare_context(context, **kwargs)
        return await self._get_template(name_).render_async(context)

    def template_sync(self, name_: str, context: dict = None, **kwargs) -> str:
        """Render a template synchronously.

        See also: #API.template().
        """
        context = self._prepare_context(context, **kwargs)
        with self._prevent_async_template_rendering():
            return self._get_template(name_).render(context)

    def template_string(
        self, source: str, context: dict = None, **kwargs
    ) -> str:
        """Render a template from a string (synchronous).

        # Parameters
        source (str): a template given as a string.

        For other parameters, see #API.template().
        """
        context = self._prepare_context(context, **kwargs)
        with self._prevent_async_template_rendering():
            template = self._templates.from_string(source=source)
            return template.render(context)
