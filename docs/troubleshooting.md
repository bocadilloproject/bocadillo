# Troubleshooting

Solutions to common or potentially confusing problems are documented here.

## ASGI 'lifespan' protocol appears unsupported

Uvicorn 7.0+ outputs this if an exception occurred during application startup. You can make Uvicorn log the exception by passing `--lifespan=on`, e.g.:

```bash
uvicorn myproject.asgi:app --lifespan=on
```

In particular, this may occur if you use Bocadillo 0.14+ and did not call `configure()` before serving the application (see [Configuration](/guides/architecture/app.md#configuration)).
