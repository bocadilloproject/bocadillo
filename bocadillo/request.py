from json import JSONDecodeError
import typing

from starlette.requests import Request as _Request, ClientDisconnect as _CD


ClientDisconnect = _CD


class Request(_Request):
    """The request object, passed to HTTP views and typically named `req`.

    This is a subclass of [`Starlette.requests.Request`][starlette-request]. As a result, all methods and attributes on Starlette's `Request` are available on this class. Additional or redefined members are documented here.

    For usage tips, see [Requests (Guide)](/guide/requests.md).

    [starlette-request]: https://www.starlette.io/requests/

    # Methods
    `__aiter__`:
        shortcut for `.stream()`. Allows to process the request body in
        byte chunks using `async for chunk in req: ...`.
    """

    async def json(self) -> typing.Any:
        """Parse the request body as JSON.

        # Returns
        json (dict): the result of `json.loads(await self.body())`.

        # Raises
        HTTPError(400): if the JSON is malformed.
        """
        try:
            return await super().json()
        except JSONDecodeError:
            from .errors import HTTPError  # prevent circular imports

            raise HTTPError(400, detail="JSON is malformed.")

    async def __aiter__(self) -> typing.AsyncGenerator[bytes, None]:
        async for chunk in self.stream():
            yield chunk
