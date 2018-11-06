from typing import Callable, Type, Union, List, Optional

from .constants import ALL_HTTP_METHODS
from .request import Request
from .response import Response


class BaseView:
    """Base view interface."""

    def get(self, request: Request, response: Response, **kwargs):
        raise NotImplementedError

    def post(self, request: Request, response: Response, **kwargs):
        raise NotImplementedError

    def put(self, request: Request, response: Response, **kwargs):
        raise NotImplementedError

    def patch(self, request: Request, response: Response, **kwargs):
        raise NotImplementedError

    def delete(self, request: Request, response: Response, **kwargs):
        raise NotImplementedError


CallableView = Callable[[Request, Response, dict], None]
ClassView = Type[BaseView]
View = Union[CallableView, ClassView]


def get_view_name(view: CallableView, base: Optional[ClassView] = None) -> str:
    return '.'.join(part.__name__ for part in (base, view) if part)


def get_declared_method_views(view_cls: ClassView) -> List[CallableView]:
    views: List[CallableView] = []
    for method in ALL_HTTP_METHODS:
        method_view_name = method.lower()
        if hasattr(view_cls, method_view_name):
            views.append(getattr(view_cls, method_view_name))
    return views
