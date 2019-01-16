# bocadillo.error_handlers

## error_to_html
```python
error_to_html(req: bocadillo.request.Request, res: bocadillo.response.Response, exc: bocadillo.errors.HTTPError)
```
Convert an exception to an HTML response.

The response contains a `<h1>` tag with the error's `title` and,
if provided, a `<p>` tag with the error's `detail`.

__Example__


```html
<h1>403 Forbidden</h1>
<p>You do not have the permissions to perform this operation.</p>
```

## error_to_media
```python
error_to_media(req: bocadillo.request.Request, res: bocadillo.response.Response, exc: bocadillo.errors.HTTPError)
```
Convert an exception to a media response.

The response contains the following items:

- `error`: the error's `title`
- `status`: the error's `status_code`
- `detail`: the error's `detail` (if provided)

__Example__


```json
{
    "error": "403 Forbidden",
    "status": 403,
    "detail": "You do not have the permissions to perform this operation."
}
```

## error_to_text
```python
error_to_text(req: bocadillo.request.Request, res: bocadillo.response.Response, exc: bocadillo.errors.HTTPError)
```
Convert an exception to a plain text response.

The response contains a line with the error's `title` and, if provided,
a line for the error's `detail`.

__Example__

```
403 Forbidden
You do not have the permissions to perform this operation.
```

