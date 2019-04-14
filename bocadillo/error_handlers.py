from .request import Request
from .response import Response
from .errors import HTTPError


# Built-in HTTP error handlers.


async def error_to_html(req: Request, res: Response, exc: HTTPError):
    """Convert an exception to an HTML response.

    The response contains a `<h1>` tag with the error's `title` and,
    if provided, a `<p>` tag with the error's `detail`.

    # Example

    ```html
    <h1>403 Forbidden</h1>
    <p>You do not have the permissions to perform this operation.</p>
    ```
    """
    res.status_code = exc.status_code
    html = f"<h1>{exc.title}</h1>"
    if exc.detail:
        html += f"\n<p>{exc.detail}</p>"
    res.html = html


async def error_to_json(req: Request, res: Response, exc: HTTPError):
    """Convert an exception to a JSON response.

    The response contains the following items:

    - `error`: the error's `title`
    - `status`: the error's `status_code`
    - `detail`: the error's `detail` (if provided)

    # Example

    ```json
    {
        "error": "403 Forbidden",
        "status": 403,
        "detail": "You do not have the permissions to perform this operation."
    }
    ```
    """
    res.status_code = exc.status_code
    data = {"error": exc.title, "status": exc.status_code}
    if exc.detail:
        data["detail"] = exc.detail
    res.json = data


async def error_to_text(req: Request, res: Response, exc: HTTPError):
    """Convert an exception to a plain text response.

    The response contains a line with the error's `title` and, if provided,
    a line for the error's `detail`.

    # Example
    ```
    403 Forbidden
    You do not have the permissions to perform this operation.
    ```
    """
    res.status_code = exc.status_code
    text = exc.title
    if exc.detail:
        text += f"\n{exc.detail}"
    res.text = text
