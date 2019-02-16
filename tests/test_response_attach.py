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


def _get_disposition(filename: str) -> str:
    return f"attachment; filename='{filename}'"


def test_file_response(api: API, txt: Path):
    @api.route("/")
    async def index(req, res):
        res.attach(str(txt))

    response = api.client.get("/")
    assert response.status_code == 200
    assert response.text == txt.read_text()
    assert response.headers["content-disposition"] == _get_disposition(txt.name)


def test_if_file_does_not_exist_then_fail(api: API):
    @api.route("/")
    async def index(req, res):
        res.attach("doesnotexist.txt")

    with pytest.raises(RuntimeError) as ctx:
        api.client.get("/")

    assert "does not exist" in str(ctx.value)


def test_manual_attach(api: API):
    @api.route("/")
    async def index(req, res):
        res.attach(content="hi files", filename="hello.txt")

    response = api.client.get("/")
    assert response.status_code == 200
    assert response.text == "hi files"
    assert response.headers["content-disposition"] == _get_disposition(
        "hello.txt"
    )


@pytest.mark.parametrize("field", ["content", "filename"])
def test_manual_attach_if_no_content_or_filename_then_fail(api: API, field):
    kwargs = {"content": "hi files", "filename": "hello.txt"}
    kwargs.pop(field)

    @api.route("/")
    async def index(req, res):
        res.attach(**kwargs)

    with pytest.raises(AssertionError):
        api.client.get("/")
