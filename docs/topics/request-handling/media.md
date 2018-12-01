# Media

In Bocadillo, **media** refers to data of a specific format — e.g. JSON or YAML — that generally needs some kind of serialization before being sent over the wire.

Each Bocadillo application has a **media type** (a valid [MIME type]) which determines how values given to `res.media` (see [Responses](../responses.md)) are handled.

The default media type is `application/json`.

## Relationship with `res.media`

When setting `res.media`, Bocadillo does two things:

- Set the `Content-Type` header to the application's `media_type`.
- Serialize the given value and use the resulting string as the response content.

## Configuring the media type

You can configure an application's media type by:

- Passing the `media_type` argument when building the `API` object:

```python
import bocadillo
api = bocadillo.API(media_type='application/json')
```

- Setting the `media_type` attribute directly on the `API` object:

```python
import bocadillo
api = bocadillo.API()
api.media_type = 'application/json'
```

::: warning
If `media_type` is not one of the built-in or custom media types,
an `UnsupportedMediaType` exception is raised.
:::

## Built-in media types

| Format | `media_type` | Constant* | Handler |
|------------|--------------|----------|---------|
| Plain text | `text/plain` | `PLAIN_TEXT` | `str` |
| HTML | `text/html` | `HTML` | `str` |
| JSON | `application/json` | `JSON` | `json.dumps` |

*Accessible on the `bocadillo.Media` object.

## Custom media types

Bocadillo stores media handlers in the `api.media_handlers` dictionary, which maps a `media_type` to a **media handler**, i.e. a function with the following signature: `(Any) -> str`.

You can manipulate this dictionary to add, remove or replace media handlers.

```python
def handle_foo(value):
    return f'foo: {value}'

# Add or replace
api.media_handlers['application/x-foo'] = handle_foo

# Remove
api.media_handlers.pop('application/json')

# Replace entirely (/!\ removes pre-existing media handlers)
api.media_handlers = {
    'application/x-foo': handle_foo,
}
```

For a practical example, read our [how to register extra media handlers](../../how-to/extra-media-handlers.md) guide.

[MIME type]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
