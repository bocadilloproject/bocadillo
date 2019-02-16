from pathlib import Path
from typing import Optional

import pytest

from bocadillo import API


@pytest.fixture
def txt(tmp_path) -> Path:
    txt = tmp_path / "hello.txt"
    txt.write_text("hi files")
    assert txt.name == "hello.txt"
    return txt


@pytest.mark.parametrize("attach", (True, False, None))
def test_file_response(api: API, txt: Path, attach: bool):
    kwargs = {} if attach is None else {"attach": attach}

    @api.route("/")
    async def index(req, res):
        res.file(str(txt), **kwargs)

    response = api.client.get("/")
    assert response.status_code == 200
    assert response.text == txt.read_text()
    if attach is False:
        assert "content-disposition" not in response.headers
    else:
        assert (
            response.headers["content-disposition"]
            == f"attachment; filename='{txt.name}'"
        )


def test_if_file_does_not_exist_then_fail(api: API):
    @api.route("/")
    async def index(req, res):
        res.file("doesnotexist.txt")

    with pytest.raises(RuntimeError) as ctx:
        api.client.get("/")

    assert "does not exist" in str(ctx.value)
