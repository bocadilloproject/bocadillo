# Static files

Bocadillo uses [WhiteNoise](http://whitenoise.evans.io/en/stable/) to serve static assets for you in an efficient manner.

## Basic usage

Place files in the `static` folder at the root location, and they will be available at the corresponding URL:

```css
/* static/css/styles.css */
h1 {
  color: red;
}
```

```bash
curl "http://localhost:8000/static/css/styles.css"
```

```
h1 { color: red; }
```

## Static files location

By default, static assets are served at the `/static/` URL root and are searched for in a `static/` directory relative to where the app is executed. For example:

```
.
├── static
│   └── css
│       └── styles.css
└── myproject
    ├── app.py
    └── settings.py
```

You can modify the static files directory using the `STATIC_DIR` setting:

```python
# myproject/settings.py
STATIC_DIR = "staticfiles"
```

To modify the root URL path, use the `STATIC_ROOT` setting:

```python
# myproject/settings.py
STATIC_ROOT = "assets"
```

::: tip
If the `STATIC_DIR` does not exist, Bocadillo won't attempt to serve assets from it, and no errors/warnings will be raised.
:::

## Extra static files directories

You can serve extra static directories using [`app.mount()`](/api/applications.md#mount) and the [`static`](/api/staticfiles.md#static) helper:

```python
from bocadillo import static

app.mount(prefix="assets", app=static("assets"))
```

## WhiteNoise configuration

You can pass any extra [WhiteNoise configuration attributes](http://whitenoise.evans.io/en/stable/base.html#configuration-attributes) via the `STATIC_CONFIG` setting.

For example, to set the time browsers and proxies should cache files to 30 seconds, use:

```python
# myproject/settings.py
STATIC_CONFIG = {"max_age": 30}
```

## Disabling static files

To prevent Bocadillo from serving static files altogether, use:

```python
# myproject/settings.py
STATIC_DIR = None
```
