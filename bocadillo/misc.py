from os.path import join, dirname, abspath
from typing import Callable

assets_dir = join(dirname(abspath(__file__)), "assets")


# TODO make async using aiofiles?
def read_asset(filename: str) -> str:
    with open(join(assets_dir, filename), "r") as f:
        return f.read()


def overrides(original: Callable) -> Callable:
    def decorate(func):
        func.__doc__ = original.__doc__
        return func

    return decorate
