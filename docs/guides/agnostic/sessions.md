# Cookie-based sessions <Badge text="0.13+"/>

Bocadillo has support for signed cookie-based HTTP sessions. These are available to use both in HTTP and WebSocket views as a simple means of **persisting data between requests**. This data is stored in [cookies] that the client's web browser sends back when they make subsequent requests to the server.

[cookies]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies

## Security considerations

When misused, cookies can be vectors for several attacks including Man-in-the-Middle, [Cross-Site Scripting](/discussions/security.md#cross-site-scripting-xss) (XSS) and [Cross-Site Request Forgery](/discussions/security.md#cross-site-request-forgery-csrf) (CSRF).

The first one can be mitigated by using [HTTPS](/discussions/security.md#https). XSS is mostly mitigated by the `httponly` flag set by Bocadillo when setting up the cookie.

However, **we do not provide any CSRF mitigation at the moment**. For this reason, **we strongly advise against using cookie-based sessions to store sensitive data**, e.g. user credentials.

As an additional security measure, though, Bocadillo uses **signed cookies** to make sure that cookies only contain what you (i.e. the server-side application) have put in it. In other words, if the cookie content was changed by a malicious client, Bocadillo will tell and prevent it from being processed.

This is only possible thanks to the use of a **secret key**. As for anything _secret_, you should store it in a safe place. An environment variable is a good choice, and we make it easy to retrieve it from there, as described later.

## Prerequisites

The sessions feature requires to install Bocadillo with the `[sessions]` extra:

```bash
pip install bocadillo[sessions]
```

## Enabling sessions

To enable sessions, pass `enable_sessions=True` when instanciating the application instance:

```python
from bocadillo import App

app = App(enable_sessions=True)
```

## Configuring sessions

The most important session configuration item is the **secret key**. It is read from the `SECRET_KEY` environment variable, or from the `sessions_config` passed to the [`App`](/api/applications.md#app). It must be set and non-empty if sessions are enabled.

::: tip
You can use tools like the [Django Secret Key Generator](https://www.miniwebtool.com/django-secret-key-generator/) to generate strong enough secret keys.
:::

The `sessions_config` parameter can be used to pass any configuration items described in Starlette's [SessionsMiddleware](https://www.starlette.io/middleware/#sessionmiddleware).

For example, pass `{"https_only": True}` to restrict cookie-based sessions to requests made over HTTPS:

```python
app = App(
    enable_sessions=True,
    sessions_config={"https_only": True},
)
```

## Using sessions

Once sessions are enabled and configured, use the `req.session` dictionary to retrieve and store session data.

In the following example, we use a cookie-based session to store the ID of the last todo item that was sent to the client and only send the new todo items. It assumes that the `SECRET_KEY` environment variable is set.

<<<@/docs/guides/agnostic/snippets/sessions.py
