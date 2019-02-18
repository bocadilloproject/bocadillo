from functools import wraps
from typing import Callable

import warnings


def deprecated(since: str, removal: str, alternative: str) -> Callable:
    """Signal that a function is deprecated.

    # Parameters
    since (str): version when the function has been deprecated.
    removal (str): version when the function will be removed.
    alternative (str): what should be used instead.
    """

    def get_message(func: Callable) -> str:
        return (
            f"{func.__name__} was deprecated in v{since}, and will "
            f"be removed in v{removal}. Please use {alternative} instead."
        )

    def add_warning(func: Callable) -> Callable:
        @wraps(func)
        def with_warning(*args, **kwargs):
            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn(
                get_message(func), category=DeprecationWarning, stacklevel=2
            )
            warnings.simplefilter("default", DeprecationWarning)
            return func(*args, **kwargs)

        return with_warning

    return add_warning
