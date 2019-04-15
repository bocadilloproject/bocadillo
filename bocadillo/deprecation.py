import warnings
from functools import partial, wraps
from inspect import cleandoc, isclass
import typing

_F = typing.TypeVar("_F", bound=typing.Callable)
_T = typing.TypeVar("_T")
_FT = typing.Union[_F, typing.Type[_T]]


def deprecated(
    since: str,
    removal: str,
    alternative: typing.Union[str, typing.Tuple[str, str]],
    update_doc: bool = True,
    warn_on_instanciate: bool = False,
) -> typing.Callable:
    """Mark a function or a class as deprecated.

    The function or class will raise a `DeprecationWarning` when called and
    its docstring will be updated with a warning special container to be
    rendered in the API reference.

    # Parameters
    since (str):
        version when the function has been deprecated.
    removal (str):
        version when the function will be removed.
    alternative (str or tuple):
        what should be used instead. Can be a string (name of the alternative)
        or a tuple of two strings (name and a link to the API reference).
    link (str):
        a link to the API reference for the alternative.
    update_doc (bool):
        whether the object's docstring should be updated.
    warn_on_instanciate (bool):
        if the object is a class, whether a deprecation warning should be
        sent when instanciating it.    
    """

    if isinstance(alternative, tuple):
        name, link = alternative
        alternative_formatted = f"[`{name}`]({link})"
        alternative = name
    else:
        alternative_formatted = f"`{alternative}`"

    def get_message(obj: _FT, strip: bool = False) -> str:
        obj_name = obj.__name__ if strip else f"`{obj.__name__}`"
        alt = alternative if strip else alternative_formatted
        return (
            f"{obj_name} was **deprecated** in v{since}, and will "
            f"be **removed** in v{removal}. Please use {alt} instead."
        )

    def show_warning(obj: _FT):
        warnings.simplefilter("always", DeprecationWarning)
        warnings.warn(
            get_message(obj, strip=True),
            category=DeprecationWarning,
            stacklevel=2,
        )
        warnings.simplefilter("default", DeprecationWarning)

    def get_doc_warning(obj: _FT) -> str:
        return f"::: warning DEPRECATED\n{get_message(obj)}\n:::"

    def add_warning(obj: _FT) -> _FT:
        if isclass(obj):
            cls = typing.cast(typing.Type, obj)

            if warn_on_instanciate:

                class wrapped(cls):  # type: ignore
                    def __init__(self, *args, **kwargs):
                        show_warning(obj)
                        super().__init__(*args, **kwargs)

                # No equivalent for @wraps for classes? Update name and docs.
                wrapped.__name__ = cls.__name__
                wrapped.__doc__ = cls.__doc__

            else:
                wrapped = cls  # type: ignore

        else:
            func = typing.cast(typing.Callable, obj)

            @wraps(func)  # type: ignore
            def wrapped(*args, **kwargs):
                show_warning(func)
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
        alternative: typing.Union[str, tuple]
        if fragment is not None:
            alternative = (self._obj_root + name, self._doc_root + fragment)
        else:
            alternative = self._obj_root + name
        return self._factory(alternative=alternative)
