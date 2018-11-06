import pytest

import bocadillo


@pytest.fixture
def api():
    return bocadillo.API()
