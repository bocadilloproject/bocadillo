import random

from starlette.concurrency import run_in_threadpool

from bocadillo import App, configure

app = App()
configure(app)


def sort_random_numbers(n):
    numbers = [random.random() for _ in range(n)]
    return sorted(numbers)


@app.route("/work/{exp}")
async def work(req, res, exp):
    await run_in_threadpool(sort_random_numbers, 10 ** int(exp))
    res.text = "Done"


@app.route("/check")
async def check(req, res):
    res.text = "OK"
