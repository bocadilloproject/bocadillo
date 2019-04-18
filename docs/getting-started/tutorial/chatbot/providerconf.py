"""Providers configuration.

See: https://bocadilloproject.github.io/guides/injection/
"""
from contextlib import contextmanager

from bocadillo import provider


@provider(scope="app")
def diego():
    from .bot import diego

    return diego


@provider(scope="app")
def clients():
    return set()


@provider
def save_client(clients):
    @contextmanager
    def _save(ws):
        clients.add(ws)
        try:
            yield ws
        finally:
            clients.remove(ws)

    return _save
