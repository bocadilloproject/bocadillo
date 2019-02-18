import warnings
from functools import wraps, partial
from inspect import cleandoc, isclass
from typing import Callable, cast, TypeVar, Union, Type, Tuple

_T = TypeVar("_T", bound=Union[Type, Callable])


def deprecated(
    since: str,
    removal: str,
    alternative: Union[str, Tuple[str, str]],
    update_doc: bool = True,
) -> Callable:
    """Mark a function or a class as deprecated.

    The function or class will raise a `DeprecationWarning` when called and
    its docstring will be updated with a warning special container to be
    rendered in the API reference.

    # Parameters
    since (str): version when the function has been deprecated.
    removal (str): version when the function will be removed.
    alternative (str or tuple):
        what should be used instead. Can be a string (name of the alternative)
        or a tuple of two strings (name and a link to the API reference).
    link (str): a link to the API reference for the alternative.
    update_doc (bool): whether the object's docstring should be updated.
    """

    if isinstance(alternative, tuple):
        name, link = alternative
        alternative_formatted = f"[`{name}`]({link})"
        alternative = name
    else:
        alternative_formatted = f"`{alternative}`"

    def get_message(obj: _T, strip: bool = False) -> str:
        obj_name = obj.__name__ if strip else f"`{obj.__name__}`"
        alt = alternative if strip else alternative_formatted
        return (
            f"{obj_name} was **deprecated** in v{since}, and will "
            f"be **removed** in v{removal}. Please use {alt} instead."
        )

    def get_doc_warning(obj: _T) -> str:
        return f"::: warning DEPRECATED\n{get_message(obj)}\n:::\n"

    def add_warning(obj: _T) -> _T:
        if isclass(obj):
            wrapped = obj
        else:
            func = cast(Callable, obj)

            @wraps(func)  # type: ignore
            def wrapped(*args, **kwargs):
                warnings.simplefilter("always", DeprecationWarning)
                warnings.warn(
                    get_message(func, strip=True),
                    category=DeprecationWarning,
                    stacklevel=2,
                )
                warnings.simplefilter("default", DeprecationWarning)
                return func(*args, **kwargs)

        if update_doc:
            header, _, body = cleandoc(obj.__doc__ or "").partition("\n")
            wrapped.__doc__ = "\n\n".join([header, get_doc_warning(obj), body])

        return wrapped

    return add_warning


class ReplacedBy:
    def __init__(
        self, since: str, removal: str, obj_root: str = "", doc_root: str = ""
    ):
        self._obj_root = obj_root
        self._doc_root = doc_root
        self._factory = partial(deprecated, since=since, removal=removal)

    def __call__(self, name: str, fragment: str = None):
        alternative: Union[str, tuple]
        if fragment is not None:
            alternative = (self._obj_root + name, self._doc_root + fragment)
        else:
            alternative = self._obj_root + name
        return self._factory(alternative=alternative)
