# Static files

Bocadillo uses [WhiteNoise](http://whitenoise.evans.io/en/stable/) to serve
static assets for you in an efficient manner.

## Basic usage

Place files in the `static` folder at the root location,
and they will be available at the corresponding URL:

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

By default, static assets are served at the `/static/` URL root and are
searched for in a `static/` directory relative to where the app is executed.
For example:

```
.
├── app.py
└── static
    └── css
        └── styles.css
```

You can modify the static files directory using the `static_dir` option:

```python
app = App(static_dir='staticfiles')
```

To modify the root URL path, use `static_root`:

```python
app = App(static_root='assets')
```

::: tip
If the `static_dir` does not exist, Bocadillo won't attempt to serve assets from
it, and no errors nor warnings will be raised.
:::

## Extra static files directories

You can serve other static directories using `app.mount()` and the
`static` helper:

```python
from bocadillo import App, static

app = App()

# Serve more static files located in the assets/ directory
app.mount(prefix='assets', app=static('assets'))
```

## WhiteNoise configuration

You can pass any extra [WhiteNoise configuration attributes](http://whitenoise.evans.io/en/stable/base.html#configuration-attributes) via the `static_config` parameter.

For example, to set the time browsers and proxies should cache files to 30 secondes, use:

```python
app = App(static_config={"max_age": 30})
```

## Disabling static files

To prevent Bocadillo from serving static files altogether,
you can use:

```python
app = App(static_dir=None)
```
