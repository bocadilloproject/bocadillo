# The application class

The main object you'll manipulate in Bocadillo is the `App` object, an
ASGI-compliant application. This page will explain the basics of running and configuration an application.

## Running a Bocadillo app

To run a Bocadillo app, either:

- Run the application script:

```python
# app.py
import bocadillo

app = bocadillo.App()

if __name__ == '__main__':
    app.run()
```

```bash
python app.py
```

- Give it to [uvicorn](https://www.uvicorn.org)
  (an ASGI server installed with Bocadillo) as `path.to.module:app_variable`:

```bash
uvicorn app:app
```

## Debug mode

You can run an application in debug mode to enable in-browser tracebacks and hot reloading.

::: danger
Debug mode discloses sensitive information about your application runtime. We strongly recommend to disable it in production.
:::

Debug mode can be enabled:

- Programmatically:

```python
app.run(debug=True)
```

::: warning CAVEAT
For uvicorn to be able to find the application object, you should declare it as `app` in the application script — like we do on this page.

If you can't, you should tell uvicorn by passing the `declared_as` argument:

```python
application.run(debug=True, declared_as="application")
```

:::

- From the command line by passing the `--debug` flag to uvicorn:

```bash
uvicorn app:app --debug
```

## Configuring host and port

By default, Bocadillo serves your app on `127.0.0.1:8000`,
i.e. `localhost` on port 8000.

To customize the host and port, you can:

- Specify them on `app.run()`:

```python
app.run(host='mydomain.org', port=5045)
```

- Set the `PORT` environment variable. Bocadillo will pick
  it up and automatically use the host `0.0.0.0` to accept all existing hosts
  on the machine. This is especially useful when running the app in a
  container or on a cloud hosting service. If needed, you can still specify
  the `host` on `app.run()`.

## Allowed hosts

By default, a Bocadillo application can run on any host. To specify which hosts are allowed, use `allowed_hosts`:

```python
app = bocadillo.App(allowed_hosts=['mysite.com'])
```

If a non-allowed host is used, all requests will return a 400 error.
