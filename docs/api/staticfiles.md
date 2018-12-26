# bocadillo.staticfiles

## static
```python
static(directory: str) -> Callable[[dict, Callable], List[bytes]]
```
Return a WSGI app that serves static files under the given directory.

Powered by WhiteNoise.

__Parameters__

- __directory (str)__:
    the path to a directory from where static files should be served.
    If the directory does not exist, no files will be served.

__Returns__

`app (WSGIApp)`: a WSGI-compliant application.

__See Also__

- [WhiteNoise](http://whitenoise.evans.io)
- [WSGI](https://wsgi.readthedocs.io)

