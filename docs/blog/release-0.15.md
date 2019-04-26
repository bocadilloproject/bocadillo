---
title: "Bocadillo 0.15 released!"
description: "This release brings support for ASGI3 to Bocadillo. We've also seized this opportunity to revamp how middleware works."
date: 2019-04-26
author: Florimond Manca
layout: Post
---

If you have any questions or feedback about this release, feel free to [get in touch](/faq.md#getting-in-touch)!

[[toc]]

## ASGI3

[ASGI](https://asgi.readthedocs.io/en/latest/), or Asynchronous Server Gateway Interface, is the protocol that enables communication between Bocadillo applications and asynchronous web servers such as [uvicorn](https://www.uvicorn.org).

A few weeks ago, [ASGI version 3.0 was released](https://www.encode.io/reports/february-2019/), and support was incrementally added to uvicorn and Starlette. Although support for ASGI3 in Starlette is still in beta, we're confident enough that it should land in stable version soon without major changes.

As a result, **Bocadillo applications implement ASGI3** as of 0.15.0.

**As a Bocadillo user, this change should not impact you**. This is because Bocadillo abstracts away the details of communicating with a web server. (The only exception to this is if you've been using ASGI middleware — see below.) You will only need to use uvicorn 0.6.x — but it should upgrade automatically when running `pip install -U bocadillo`.

**What's next?** The async web ecosystem is slowly migrating from ASGI2 to ASGI3. As such, you may find some libraries you use aren't compatible yet with ASGI3. In that case, please stick to Bocadillo 0.14.x for now, or find an alternative solution.

## Middleware

We brought a few small changes to how middleware works.

::: tip
You shouldn't be impacted by these changes unless you wrote HTTP or ASGI middleware yourself.
:::

### ASGI middleware

The `ASGIMiddleware` base class was removed entirely. We obviously still support ASGI middleware — via `app.add_asgi_middleware()` for instance — but instead of relying on a base class, you must now implement the ASGI protocol yourself.

Please refer to [Writing middleware](/how-to/middleware.md#asgi-middleware) for details.

### App initialisation

We used to encourage app initialisation via middleware by passing the `App` instance to the middleware's constructor.

However, with the arrival of [plugins](/guides/architecture/plugins.md) in 0.14, we now have a dedicated (and more scalable) way to perform application initialisation.

For this reason, the constructors of middleware classes aren't given the `App` instance anymore.

If a middleware is associated to some kind of initialisation or configuration-related conditional logic, consider building a plugin on top of it.
