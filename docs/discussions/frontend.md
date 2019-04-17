# Frontend frameworks

Modern web applications typically consist of a _backend_ and a _frontend_. Bocadillo is a backend framework, but it's dead simple to integrate with modern frontend JavaScript frameworks.

## Guidelines

Frontend frameworks generally have their own development tooling, including command line tools, hot reload, etc. Based on this assumption, here are our recommendations:

- **In development**, run 2 separate servers in development: one for Bocadillo, one for the frontend.
- **In production**, have Bocadillo serve the frontend build. This is efficient enough for most use cases (thanks to WhiteNoise), and can be achieved by mounting the build directory as an [extra static files directory](/guides/http/static-files.md#extra-static-files-directories).

## Example repos

The following example repos show how to get a **development setup** ready and **serve build artefacts for production** using Bocadillo. Feel free to check them out, fork them, and hack them away! 🚀

| Frontend framework | Example repo    |
| :----------------- | :-------------- |
| React              | [react-example] |

[react-example]: https://github.com/bocadilloproject/react-example

::: tip CONTRIBUTING
Missing your favorite framework? Discuss it with us by <open-issue text="opening an issue"/>. We'd be glad to setup and work together on additional official example repos.
:::
