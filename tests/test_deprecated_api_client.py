# DEPRECATED from 0.13 to 0.14

import pytest

from bocadillo import App


def test_throws_deprecation_warnings(app: App):
    with pytest.deprecated_call():
        _ = app.client
