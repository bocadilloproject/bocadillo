from contextlib import contextmanager
from typing import cast

try:
    from jinja2 import Environment, FileSystemLoader, Template
except ImportError as exc:
    raise ImportError(
        "`jinja2` is not installed. "
        "Have you installed Bocadillo using `bocadillo[templates]`?"
    ) from exc


class Jinja2Engine:
    def __init__(self, directory: str, context: dict):
        self._directory = directory
        self._globals = context
        self._environment = Environment(
            loader=FileSystemLoader([self.directory]), autoescape=True
        )
        self._environment.globals.update(self._globals)

    @property
    def _loader(self) -> FileSystemLoader:
        return cast(FileSystemLoader, self._environment.loader)

    @property
    def directory(self) -> str:
        return self._directory

    @directory.setter
    def directory(self, directory: str):
        self._directory = directory
        self._loader.searchpath = [self._directory]  # type: ignore

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

    async def render(self, filename: str, *args, **kwargs) -> str:
        with self._enable_async():
            return await self._get_template(filename).render_async(
                *args, **kwargs
            )

    def render_sync(self, filename: str, *args, **kwargs) -> str:
        return self._get_template(filename).render(*args, **kwargs)

    def render_string(self, source: str, *args, **kwargs) -> str:
        template = self._environment.from_string(source=source)
        return template.render(*args, **kwargs)
