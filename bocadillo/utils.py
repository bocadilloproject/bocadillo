import os
from contextlib import contextmanager


@contextmanager
def override_env(variable: str, value: str):
    """Context manager to temporarily override an environment variable.

    The variable is restored to its initial value (if any) when exiting the
    context.

    # Example

    ```python
    from bocadillo.utils import override_env

    with override_env("SOME_VAR", "yes"):
        ...
    ```

    # Parameters
    variable (str): the name of the environment variable.
    value (str): a temporary value for the environment variable.
    """
    initial = os.environ.get(variable, None)
    os.environ[variable] = value
    try:
        yield
    finally:
        os.environ.pop(variable)
        if initial is not None:
            os.environ[variable] = initial
