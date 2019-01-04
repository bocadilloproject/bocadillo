# bocadillo.errors

## HTTPError
```python
HTTPError(self, status: Union[int, http.HTTPStatus], detail: Any = '')
```
Raised when an HTTP error occurs.

You can raise this within a view or an error handler to interrupt
request processing.

__Parameters__

- __status (int or HTTPStatus)__:
    the status code of the error.
- __detail (any)__:
    extra detail information about the error. The exact rendering is
    determined by the configured error handler for `HTTPError`.

__See Also__

- [HTTP response status codes (MDN web docs)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)

### status_code
Return the HTTP error's status code, e.g. `404`.
### status_phrase
Return the HTTP error's status phrase, e.g. `"Not Found"`.
### title
Return the HTTP error's title, e.g. `"404 Not Found"`.
## ServerErrorMiddleware
```python
ServerErrorMiddleware(self, app: Callable[[bocadillo.request.Request, bocadillo.response.Response], Awaitable[NoneType]], handler: Callable[[bocadillo.request.Request, bocadillo.response.Response, Exception], NoneType], debug: bool = False) -> None
```
Return 500 response when an unhandled exception occurs.

Adaption of Starlette's ServerErrorMiddleware.

## HTTPErrorMiddleware
```python
HTTPErrorMiddleware(self, app: Callable[[bocadillo.request.Request, bocadillo.response.Response], Awaitable[NoneType]], debug: bool = False) -> None
```
Handler exceptions that occur while handling HTTP requests.
