# Static files

Bocadillo uses [WhiteNoise](http://whitenoise.evans.io/en/stable/) to serve
static assets for you in an efficient manner.

## Basic usage

Place files in the `static` folder at the root location,
and they will be available at the corresponding URL:

```css
/* static/css/styles.css */
h1 { color: red; }
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
api = bocadillo.API(static_dir='staticfiles')
```

To modify the root URL path, use `static_root`:

```python
api = bocadillo.API(static_root='assets')
```

## Extra static files directories

You can serve other static directories using `app.mount()` and the
`static` helper:

```python
import bocadillo

api = bocadillo.API()

# Serve more static files located in the assets/ directory
api.mount(prefix='assets', app=bocadillo.static('assets'))
```

## Disabling static files

To prevent Bocadillo from serving static files altogether,
you can use:

```python
api = bocadillo.API(static_dir=None)
```
