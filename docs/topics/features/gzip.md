# GZip

If you want to enable [GZip compression](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Encoding#Directives) to compress responses when possible, simply use:

```python
api = bocadillo.API(enable_gzip=True)
```

You can also specify the minimum bytes the response should have before compressing:

```python
api = bocadillo.API(enable_gzip=True, gzip_min_size=2048)
```
