from json import JSONDecodeError

from starlette.requests import Request as _Request

from .exceptions import HTTPError


class Request(_Request):
    """The succulent request object."""

    async def json(self):
        """Parse the request body as JSON.

        # Returns
        json (dict): the result of `json.loads(await self.body())`.

        # Raises
        HTTPError(400): if the JSON is malformed.
        """
        try:
            return await super().json()
        except JSONDecodeError:
            raise HTTPError(400, detail="JSON is malformed.")
