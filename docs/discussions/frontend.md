# Frontend frameworks

Modern web applications typically consist of a _backend_ and a _frontend_. Bocadillo is a backend framework, but it's dead simple to integrate with modern frontend JavaScript frameworks.

## Guidelines

Frontend frameworks generally have their own development tooling, including command line tools, hot reload, etc. Based on this assumption, here are our recommendations:

- **In development**: run 2 separate servers — one for Bocadillo, one for the frontend.
- **In production**, either:
  - Serve the frontend build with Bocadillo. This may be enough for smaller-scale setups, and as shown in the [react-example] repo, this can be achieved by:
    1. Mounting the build directory as an [extra static files directory](/guide/static-files.md#extra-static-files-directories).
    2. Serving the main `index.html` using [templates](/guide/templates.md).
  - **(Recommended)** Deploy Bocadillo and the frontend on two separate hosts. See also [Deployment](/discussions/deployment.md) for general hints on deploying Bocadillo applications. For the frontend, please refer to your framework's instructions.

## Example repos

The following example repos show how to get a **development setup** ready for your Bocadillo and frontend apps. Feel free to check them out, fork them, and hack them away! 🚀

| Frontend framework | Repository      | Description                                 |
| :----------------- | :-------------- | :------------------------------------------ |
| React              | [react-example] | Hello world example, with GraphQL setup.    |
| Vue.js             | [vue-example]   | URL Shortener web app, with database setup. |

[react-example]: https://github.com/bocadilloproject/react-example
[react-example@react-apollo]: https://github.com/bocadilloproject/react-example/tree/react-apollo
[vue-example]: https://github.com/bocadilloproject/vue-example

::: tip CONTRIBUTING
Missing your favorite framework? Discuss it with us by <open-issue text="opening an issue"/>. We'd be glad to setup and work together on additional official example repos.
:::
