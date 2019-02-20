# YAML media serialization

In Bocadillo, the default behavior for `res.media` is to send JSON data.

Here, we'll configure Bocadillo to serialize values set to `res.media` to [YAML] using a **custom media handler**.

1. Install [PyYaml][pyyaml] using `pip install pyyaml`
2. Write a new media handler and register it on the application:

```python
import bocadillo
import yaml

def handle_yaml(value: dict) -> str:
    return yaml.dump(value)

app = bocadillo.App()
app.media_handlers['application/x-yaml'] = handle_yaml
```

3. Use the YAML media handler, you need to configure the applications's media type to `"application/x-yaml"`. See [Configuring the media type](../guides/http/media.md#configuring-the-media-type).

[yaml]: http://yaml.org
[pyyaml]: https://pyyaml.org
