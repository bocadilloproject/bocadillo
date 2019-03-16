# Security

Bocadillo is still a young framework and, while we're building it with security in mind, you should make sure you follow common security guidelines before putting your application in production.

::: warning DISCLAIMER
Information Security is hard, and we're no experts. If you notice anything wrong with the present recommendations, please let us know, e.g. by opening an issue.
:::

## HTTPS

HTTPS encrypts the communication between the server and the client, which means no one will be able to intercept or forge packets. This typically helps in preventing Man-in-the-Middle (MITM) attacks and is a necessary condition for securing a web application. Many web browsers today even display your site as "insecure" if it does not have HTTPS.

To set up HTTPS, you need to get a certificate from a Certificate Authority (CA). [Let's Encrypt](https://letsencrypt.org) is a popular, free and open source CA. Certificates need to be regularly updated, so we recommend you use [Certbot](https://certbot.eff.org) to automate the process.

Once your certificate and key files (`.crt`, `.key`) are generated, you can provide them to your Bocadillo application either by:

- Telling [uvicorn](https://www.uvicorn.org/settings/#https) by passing the `ssl_certfile` and `ssl_keyfile` arguments to `app.run()`:

```python
app.run(ssl_certfile="path/to/server.crt", ssl_keyfile="path/to/server.key")
```

- Passing `--certfile` and `--keyfile` to Gunicorn in a production setup (see [deployment]):

```bash
gunicorn --certfile=path/to/server.crt --keyfile=path/to/server.key ...
```

If you're hosting your app via a cloud provider, refer to their documentation as they may provide a feature to set up HTTPS for you.

It can be a good idea to enable [HSTS] so that all HTTP traffic is redirected to HTTPS.

## XSS

XSS stands for **Cross-Site Scripting**. This attack consists in injecting malicious JavaScript code into HTML, such as through a `<script>` tag.

One way to prevent XSS attacks is by escaping all quotes, replacing them with their HTML equivalent.

If you're using the [templating utilities][templates] provided by Bocadillo, you are already benefiting from Jinja2 escaping strings in XML and HTML templates.

However, you should always quote attributes in order for this to work, e.g.

::: v-pre
`<input value="{{ value }}">`
:::

instead of

::: v-pre
`<input value={{ value }}>`
:::

Besides, Jinja2 cannot protect you against someone injecting malicious codes in the `href` attribute of a link tag. To prevent this, you need to set the [Content Security Policy (CSP)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy) header, which can be achieved via a middleware:

```python
from bocadillo import App, Middleware

class CSPMiddleware(Middleware):

    def after_dispatch(self, req, res):
        # Only load scripts from the origin where the response
        # is served.
        res.headers["content-security-policy"] = "default-src 'self'"

app = App()
app.add_middleware(CSPMiddleware)
```

For reference, see [Jinja2 autoescaping](http://jinja.pocoo.org/docs/2.10/app/#autoescaping).

## CSRF

CSRF stands for **Cross-Site Request Forgery**. It is a type of attack in which a malicious website or program causes an authenticated user's browser to perform an unwanted operation on a trusted site.

These attacks work because web browsers automatically provide session cookies and the IP address with the request, hence allowing the attacker to forge a request against them.

A Token-based method is a popular way to mitigate CSRF attacks.

Bocadillo does not provide any such CSRF mitigation mechanism at the moment — but session cookies are not supported yet either.

For more information on CSRF, see the OWASP [CSRF guide](<https://www.owasp.org/index.php/Cross-Site_Request_Forgery_(CSRF)>) and [Prevention Cheatsheet](<https://www.owasp.org/index.php/Cross-Site_Request_Forgery_(CSRF)_Prevention_Cheat_Sheet#Token_Based_Mitigation>).

## SQL Injection

SQL injection allows a malicious user to execute arbitrary SQL code on a database — from writing unwanted rows to dropping the entire database.

Bocadillo does not provide any official way of interacting with a database (yet), so if you decide to use a database library, you'll be on your own.

That said, preventing SQL injection is easy enough: when handling user-provided query parameters, make sure to use **parameter substitution** instead of embedding them directly into the query.

For example, don't write:

```python
symbol = "RHAT"
c.execute(f"SELECT * FROM stocks WHERE symbol = '{symbol}'")
```

Instead, use:

```python
c.execute('SELECT * FROM stocks WHERE symbol=?', ("RHAT",))
```

This will allow the underlying database driver to escape parameters for you.

Of course, this depends on the driver you're using; we recommend you refer to its documentation to make sure it supports this functionality.

The example above is taken from the [sqlite3](https://docs.python.org/3/library/sqlite3.html) documentation intro.

## Host header validation

An HTTP Host Header attack consists in a malicious user providing a fake `Host` header in a request in order to execute a potentially harmful operation. An example of this is [cache poisoning](https://www.owasp.org/index.php/Cache_Poisoning).

In order to prevent this type of attack, every Bocadillo applications has a whitelist of hosts which the `Host` header is validated against. An invalid `Host` will result in Bocadillo sending a `400 Bad Request` response.

By default, this whitelist is empty. You must configure it through the `allowed_hosts` parameter to `App` — see [allowed hosts].

[deployment]: ./deployment.md
[templates]: ../guides/agnostic/templates.md
[hsts]: ../guides/http/middleware.md#hsts
[allowed hosts]: ../guides/app.md#allowed-hosts
