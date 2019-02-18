from bocadillo import API


def test_attachment(api: API):
    @api.route("/")
    async def index(req, res):
        res.text = "hello.text"
        res.attachment = "hello.txt"

    response = api.client.get("/")
    assert response.status_code == 200
    assert (
        response.headers["content-disposition"]
        == "attachment; filename='hello.txt'"
    )
