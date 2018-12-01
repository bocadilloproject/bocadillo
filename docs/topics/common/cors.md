# CORS

Bocadillo has built-in support for [Cross-Origin Resource Sharing](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) (CORS). Adding CORS headers to responses is typically required when your API is to be accessed by web browsers.

To enable CORS, simply use:

```python
api = bocadillo.API(enable_cors=True)
```

Bocadillo has restrictive defaults to prevent security issues: empty `Allow-Origins`, only `GET` for `Allow-Methods`. To customize the CORS configuration, use `cors_config`, e.g.:

```python
api = bocadillo.API(
    enable_cors=True,
    cors_config={
        'allow_origins': ['*'],
        'allow_methods': ['*'],
    }
)
```

Please refer to Starlette's [CORSMiddleware](https://www.starlette.io/middleware/#corsmiddleware) documentation for the full list of options and defaults.
