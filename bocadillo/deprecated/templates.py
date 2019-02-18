from typing import Any, Optional

from bocadillo.deprecation import ReplacedBy
from bocadillo.templates import DEFAULT_TEMPLATES_DIR, Templates

_REPLACED_BY = ReplacedBy(
    since="0.12",
    removal="0.13",
    obj_root="bocadillo.templates.",
    doc_root="./templates.md",
)


@_REPLACED_BY("Templates", "#Templates")
class TemplatesMixin:
    """Provide templating capabilities to an application class."""

    def __init__(self, templates_dir: str = DEFAULT_TEMPLATES_DIR, **kwargs):
        super().__init__(**kwargs)
        self._templates = Templates(
            directory=templates_dir, context=self.get_template_globals()
        )

    def get_template_globals(self) -> dict:
        return {}

    @property  # type: ignore
    @_REPLACED_BY("Templates.directory", "#Templates")
    def templates_dir(self) -> Optional[str]:
        """The path where templates are searched for, or `None` if not set.

        This is built from the `templates_dir` parameter.
        """
        return self._templates.directory

    @templates_dir.setter  # type: ignore
    @_REPLACED_BY("Templates.directory", "#Templates")
    def templates_dir(self, templates_dir: str):
        self._templates.directory = templates_dir

    @_REPLACED_BY("Templates.render", "#render")
    async def template(self, name_: str, *args: dict, **kwargs: Any) -> str:
        """Render a template asynchronously.

        Can only be used within `async` functions.

        # Parameters
        name (str):
            Name of the template, located inside `templates_dir`.
            The trailing underscore avoids collisions with a potential
            context variable named `name`.
        *args (dict):
            Context variables to inject in the template.
        **kwargs (any):
            Context variables to inject in the template.
        """
        return await self._templates.render(name_, *args, **kwargs)

    @_REPLACED_BY("Templates.render_sync", "#render-sync")
    def template_sync(self, name_: str, *args: dict, **kwargs: Any) -> str:
        """Render a template synchronously.

        For parameters, see [.template()](#template).
        """
        return self._templates.render_sync(name_, *args, **kwargs)

    @_REPLACED_BY("Templates.render_string", "#render-string")
    def template_string(self, source: str, *args: dict, **kwargs: Any) -> str:
        """Render a template from a string (synchronous).

        # Parameters
        source (str): a template given as a string.
        
        For other parameters, see [.template()](#template).
        """
        return self._templates.render_string(source, *args, **kwargs)
