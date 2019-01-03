# Registering extra media handlers

In Bocadillo, the default behavior for `res.media` is to send JSON data.

To support other **media types** — such as [YAML] or [MessagePack] — you can register extra **media handlers** on your Bocadillo application.

For example, let's say we want to build an API that sends YAML data. First, install `PyYaml` using `pip install pyyaml`, then write a new media handler and register it on the API object:

```python
import bocadillo
import yaml

def handle_yaml(value: dict) -> str:
    return yaml.dump(value)

api = bocadillo.API()
api.media_handlers['application/x-yaml'] = handle_yaml
```

To use the YAML media handler, configure `media.type` on the `API` object:

```python
api.media_type = 'application/x-yaml'
```

For more information on media handlers, please refer to the [Media](../guides/http/media.md) API guide.

[YAML]: http://yaml.org
[MessagePack]: https://msgpack.org
