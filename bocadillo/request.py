from starlette.requests import Request as _Request


# Alias (for now)
class Request(_Request):
    pass
