# The application class

The main object you'll manipulate in Bocadillo is the `App` object, an
ASGI-compliant application.

## Running a Bocadillo app

To run a Bocadillo app, either run the application directly:

```python
# myapp.py
import bocadillo

app = bocadillo.App()

if __name__ == '__main__':
    app.run()
```

```bash
python myapp.py
```

Or give it to [uvicorn](https://www.uvicorn.org)
(an ASGI server installed with Bocadillo):

```bash
uvicorn myapp:app
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

## Debug mode

You can toggle debug mode (full display of traceback in responses + hot reload)
by passing `debug=True` to `app.run()`:

```python
app.run(debug=True)
```

or passing the --debug flag to uvicorn:

```bash
uvicorn myapp:app --debug
```

## Allowed hosts

By default, a Bocadillo `App` can run on any host. To specify which hosts are allowed, use `allowed_hosts`:

```python
app = bocadillo.App(allowed_hosts=['mysite.com'])
```

If a non-allowed host is used, all requests will return a 400 error.
