import pytest

from bocadillo import API


@pytest.mark.parametrize("data, status", [("{", 400), ("{}", 200)])
def test_parse_json(api: API, data: str, status: int):
    @api.route("/")
    class Index:
        async def post(self, req, res):
            res.media = await req.json()

    assert api.client.post("/", data=data).status_code == status
