# DEPRECATED: 0.13

import pytest

from bocadillo import API


def test_throws_deprecation_warnings():
    with pytest.deprecated_call():
        API()
