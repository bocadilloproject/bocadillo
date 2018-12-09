from bocadillo import API


def test_background_task_is_executed(api: API):
    executed = False

    @api.route('/')
    async def index(req, res):
        @res.background
        async def notify_executed():
            nonlocal executed
            executed = True

        res.text = 'OK'

    response = api.client.get('/')
    assert response.status_code == 200
    assert response.text == 'OK'
    assert executed


def test_background_task_is_executed_after_response_is_sent(api: API):
    @api.route('/')
    async def index(req, res):
        @res.background
        async def send_bar():
            res.text = 'BAR'

        res.text = 'FOO'

    response = api.client.get('/')
    assert response.text == 'FOO'
