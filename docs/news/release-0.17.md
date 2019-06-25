---
title: "What's new in Bocadillo 0.17"
description: "Bocadillo 0.17 is out! In this release: settings-based provider discovery, and removal of deprecated items such as recipes and the @view decorator."
date: 2019-06-25
author: Florimond Manca
layout: Post
---

If you have any questions or feedback about this release, feel free to [get in touch](https://bocadilloproject.github.io/faq.html#getting-in-touch)!

[[toc]]

## Settings-based provider discovery

Registering providers for discovery previously required to call `discover_providers()`, typically in `app.py`.

As of 0.17, you can use a more declarative approach with the new `PROVIDER_MODULES` setting.

**Note**: the previous API is still valid. See also [How are providers discovered?](https://bocadilloproject.github.io/guide/providers.html#how-are-providers-discovered).

<b-compare :labels="['0.17+ (NEW)', '< 0.17']"></b-compare>

::: slot compare-0

```python
# myproject/app.py
from bocadillo import App

app = App()
```

```python
# myproject/settings.py

PROVIDER_MODULES = ["myproject.providerconf"]
```

:::

::: slot compare-1

```python
# myproject/app.py
from bocadillo import App, discover_providers

app = App()
discover_providers("myproject.providerconf")
```

:::

::: tip
[Bocadillo CLI](https://github.com/bocadilloproject/bocadillo-cli) has been updated to use this new setting when generating a project.
:::

## Removed items

The following features and APIs were deprecated since 0.16 and have been removed:

| Removed item                | Alternative                                                                                         |
| --------------------------- | --------------------------------------------------------------------------------------------------- |
| Recipes                     | [Routers](https://bocadilloproject.github.io/guide/routers.html)                                    |
| `app.add_asgi_middleware()` | [`app.add_middleware()`](https://bocadilloproject.github.io/guide/middleware.html#using-middleware) |
| `@view`                     | [`@route(methods=...)`](https://bocadilloproject.github.io/guide/routing.html#http-methods)         |
| `@plugin`                   | [The `PLUGINS` setting](https://bocadilloproject.github.io/guide/plugins.html#using-plugins)        |
