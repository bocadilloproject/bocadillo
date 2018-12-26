# bocadillo.media

## handle_json
```python
handle_json(value: Union[dict, list]) -> str
```
Serialize a value to a JSON string using `json.dumps()`.

__Parameters__

- __value (list or dict)__: the value to serialize.

__Returns__

`json (str)`: the serialized value.

## handle_text
```python
handle_text(value: Any) -> str
```
Serialize a value to plain text using `str()`.

__Parameters__

- __value (any)__: the value to serialize.

__Returns__

`text (str)`: the serialized value.

## Media
```python
Media(self, media_type: str, handlers: Dict[str, Callable[[Any], str]] = None)
```
Registry of media handlers.

__Parameters__

- __media_type (str)__:
    The media type that will be used when serializing values.
- __handlers (dict)__:
    A mapping of media types to `(Any) -> str` callables.
    Defaults to built-in media handlers.

__Attributes__

- `JSON (str)`: `application/json`
- `PLAIN_TEXT (str)`: `text/plain`
- `HTML (str)`: `text/html`

### serialize
```python
Media.serialize(self, value: Any, media_type: str)
```
Serialize a value using the given media type.

__Parameters__

- __value (any)__: the value to be serialized.
- __media_type (str)__:
    The media type of the given value. Determines which media handler
    is used.

### type
Get or set the configured media type.

__Parameters__

- __media_type (str)__: an HTTP content type.

__Raises__

- `UnsupportedMediaType `:
    If no handler exists for the given media type.

