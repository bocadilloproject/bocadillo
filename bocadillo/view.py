from typing import Callable, Type, Union

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
