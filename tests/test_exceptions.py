from http import HTTPStatus

import pytest

from bocadillo import HTTPError


def test_http_error_status_must_be_int_or_http_status():
    HTTPError(404)
    HTTPError(HTTPStatus.NOT_FOUND)

    with pytest.raises(AssertionError) as ctx:
        HTTPError("404")

    assert "int or HTTPStatus" in str(ctx.value)
