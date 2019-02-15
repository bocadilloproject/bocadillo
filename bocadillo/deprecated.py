from contextlib import contextmanager
from typing import List, Coroutine, Optional


def fail():
    raise NotImplementedError(
        "Rendering templates from the API or Recipe has been removed. "
        "Please now use `bocadillo.templates.Templates` — "
        "docs are available at: "
        "https://bocadilloproject.github.io/guides/http/templates.html"
    )


class TemplatesMixin:
    def __init__(self, templates_dir: str = None, **kwargs):
        super().__init__(**kwargs)
        self.templates_dir = templates_dir

    async def template(self, name_: str, context: dict = None, **kwargs):
        fail()

    def template_sync(self, name_: str, context: dict = None, **kwargs):
        fail()

    def template_string(self, source: str, context: dict = None, **kwargs):
        fail()
