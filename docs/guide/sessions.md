# Cookie-based sessions

Bocadillo has support for signed cookie-based HTTP sessions. These are available to use both in HTTP and WebSocket endpoints as a simple means of **persisting data between requests**. This data is stored in [cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies) that the client's web browser automatically sends back on subsequent requests.

## Security considerations

When misused, cookies can be vectors for several attacks including Man-in-the-Middle, [Cross-Site Scripting](/discussions/security.md#xss) (XSS) and [Cross-Site Request Forgery](/discussions/security.md#csrf) (CSRF).

The first one can be mitigated by using [HTTPS](/discussions/security.md#https). XSS is mostly mitigated by the `httponly` flag set by Bocadillo when setting up the cookie.

However, **we do not provide any CSRF mitigation at the moment**. For this reason, **we strongly advise against using cookie-based sessions to store sensitive data**, e.g. user credentials.

As an additional security measure, though, Bocadillo uses **signed cookies** to make sure that cookies only contain what you (i.e. the server-side application) have put in it. In other words, if the cookie content was changed by a malicious client, Bocadillo will tell and prevent it from being processed.

This is only possible thanks to the use of a **secret key**. As for anything _secret_, you should store it in a safe place. An environment variable is a good choice, and we make it easy to retrieve it from there, as described later.

## Prerequisites

The sessions feature requires to install Bocadillo with the `[sessions]` extra:

```bash
pip install bocadillo[sessions]
```

## Enabling and configuring sessions

To enable sessions, use the `SESSIONS` setting. It should at least contain a `secret_key`. Use Starlette's `Secret` datastructure to make sure the secret key is never displayed in plain text.

```python
# myproject/settings.py
from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")
SESSIONS = {"secret_key": config("SECRET_KEY", cast=Secret)}
```

::: tip
You can use tools like the [Django Secret Key Generator](https://www.miniwebtool.com/django-secret-key-generator/) to generate strong enough secret keys.
:::

Besides, you can declare any other option available in Starlette's [SessionsMiddleware](https://www.starlette.io/middleware/#sessionmiddleware) to fine-tune how sessions behave.

For example, pass `"https_only": True` to restrict cookie-based sessions to requests made over HTTPS:

```python
# myproject/settings.py
SESSIONS = {
    # ...
    "https_only": True,
}
```

## Using sessions

Once sessions are enabled and configured, use the `req.session` dictionary to retrieve and store session data.

In the following example, we use a cookie-based session to store the ID of the last todo item that was sent to the client, and only send the new todo items for future requests.

<<<@/docs/guide/snippets/sessions/app.py

The `SECRET_KEY` environment variable must be set, so use the following to launch this example app:

```bash
SECRET_KEY=1234 uvicorn example.app:app
```
