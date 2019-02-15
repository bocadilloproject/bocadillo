# bocadillo.media

## handle_json
```python
handle_json(value: Union[dict, list]) -> str
```
A media handler that dumps a value using `json.dumps`.
## get_default_handlers
```python
get_default_handlers() -> Dict[str, Callable[[Any], str]]
```
Return the default media handlers.

- `application/json`: [handle_json](#handle-json)

## UnsupportedMediaType
```python
UnsupportedMediaType(self, media_type: str, handlers: Dict[str, Callable[[Any], str]])
```
Raised when trying to use an unsupported media type.

__Attributes__

- `media_type (str)`: the unsupported media type.
- `handlers (dict)`: the dict of supported media handlers.

