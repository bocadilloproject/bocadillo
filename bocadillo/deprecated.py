from contextlib import contextmanager
from typing import List, Coroutine, Optional


class TemplatesMixin:
    def __init__(self, templates_dir: str = None, **kwargs):
        super().__init__(**kwargs)
        self.templates_dir = templates_dir

    def _fail(self):
        raise NotImplementedError(
            "Rendering templates from the API or Recipe has been removed in "
            "v0.12.0. Please now use `bocadillo.templates.Templates`. "
            "Docs are available at: "
            "https://bocadilloproject.github.io/guides/agnostic/templates.html"
        )

    async def template(self, name_: str, context: dict = None, **kwargs):
        self._fail()

    def template_sync(self, name_: str, context: dict = None, **kwargs):
        self._fail()

    def template_string(self, source: str, context: dict = None, **kwargs):
        self._fail()
