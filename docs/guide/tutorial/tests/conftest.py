import pytest
from bocadillo import provider, create_client

from chatbot.app import app


@provider
def diego():
    class EchoDiego:
        def get_response(self, query):
            return query

    return EchoDiego()


@pytest.fixture
def client():
    return create_client(app)
