# providerconf.py
from bocadillo import provider


@provider(scope="app")
async def history():
    return []


@provider(scope="app")
async def clients():
    return set()
