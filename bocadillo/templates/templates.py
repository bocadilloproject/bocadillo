from ..api import API

from .jinja2 import Jinja2Engine

DEFAULT_TEMPLATES_DIR = "templates"


class Templates:
    """Provide templating capabilities to an application class using Jinja2.

    Parameters
    ----------
    api : bocadillo.API
    directory : str, optional
        The directory where templates should be searched for.
    context : dict, optional
        Global template variables.
    """

    def __init__(
        self,
        api: API,
        directory: str = DEFAULT_TEMPLATES_DIR,
        context: dict = None,
    ):
        self.api = api

        if context is None:
            context = {}

        context["url_for"] = self.api.url_for

        self._engine = Jinja2Engine(directory=directory, context=context)

    @property
    def directory(self) -> str:
        """The path where templates are searched for.

        This is built from the ``templates_dir`` parameter.
        """
        return self._engine.directory

    @directory.setter
    def directory(self, directory: str):
        self._engine.directory = directory

    async def render(self, filename: str, *args: dict, **kwargs: str) -> str:
        """Render a template asynchronously.

        Can only be used within ``async`` functions.

        Parameters
        ----------
        name : str
            Name of the template, located inside ``templates_dir``.
            The trailing underscore avoids collisions with a potential
            context variable named ``name``.
        *args : dict
            Context variables to inject in the template.
        *kwargs : str
            Context variables to inject in the template.
        """
        return await self._engine.render(filename, *args, **kwargs)

    def render_sync(self, filename: str, *args: dict, **kwargs: str) -> str:
        """Render a template synchronously.

        See Also
        ---------
        ``Templates.render`` for the accepted arguments.
        """
        return self._engine.render_sync(filename, *args, **kwargs)

    def render_string(self, source: str, *args: dict, **kwargs: str) -> str:
        """Render a template from a string (synchronously).

        Parameters
        ----------
        source (str): a template given as a string.

        See Also
        --------
        ``Templates.render`` for other accepted arguments.
        """
        return self._engine.render_string(source, *args, **kwargs)
