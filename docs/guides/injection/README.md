# Introduction to providers

<Badge text="experimental" type="warn"/> <Badge text="0.13+"/>

In a Bocadillo application, views typically need to access **resources** or **services** to fulfill a client's request. For example, they may need to query a database, or interact with a disk-based cache.

Yet, views shouldn't have to care about _how_ those resources are assembled, provided, or cleaned up.

To address this issue, **providers** bring an explicit, modular and flexible way to **inject resources into views**.

The look and feel for the providers API was heavily inspired by [pytest fixtures](https://docs.pytest.org/en/latest/provider.html). However, providers are not specifically meant for testing (although they do enhance testability). Instead, you can think of providers as a **runtime dependency injection mechanism**.

::: tip GOOD TO KNOW
The implementation of providers in Bocadillo relies on [aiodine](https://github.com/bocadilloproject/aiodine), an officially supported async-first dependency injection library. In fact, Bocadillo's dependency injection framework is mostly a wrapper around aiodine, with slight changes made to accomodate Bocadillo as a web framework.

This guide summarizes common usage, but we also encourage you to check out aiodine's documentation (or even its source code) if you feel the need.
:::
