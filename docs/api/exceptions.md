# bocadillo.exceptions

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
## UnsupportedMediaType
```python
UnsupportedMediaType(self, media_type: str, available: List[str])
```
Raised when trying to use an unsupported media type.

__Parameters__

- __media_type (str)__:
    the unsupported media type.
- __available (list of str)__:
    a list of supported media types.

## TemplateNotFound
```python
TemplateNotFound(self, name, message=None)
```
Raised when loading a non-existing template.

This is an alias to
[jinja2.TemplateNotFound](http://jinja.pocoo.org/docs/2.10/api/#jinja2.TemplateNotFound).

