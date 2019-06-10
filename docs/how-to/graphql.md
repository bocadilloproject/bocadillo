# GraphQL with Tartiflette

[GraphQL](https://graphql.org/) is an API query language, often presented as a complement to regular REST API endpoints. The GraphQL documentation reads:

> GraphQL [...] gives clients the power to ask for exactly what they need and nothing more, makes it easier to evolve APIs over time, and enables powerful developer tools.

If you want to build a GraphQL API with Bocadillo, we recommend using:

- [Tartiflette](https://tartiflette.io): a Python asynchronous GraphQL engine built on `libgraphqlparser`.
- [tartiflette-starlette](https://github.com/tartiflette/tartiflette-starlette): an ASGI wrapper for Tartiflette featuring a built-in **GraphiQL client**.

::: tip SEE ALSO

- For an introduction to GraphQL, read the official [Introduction to GraphQL](https://graphql.org/learn/).
- For a complete example project using Tartiflette and `tartiflette-starlette`, including a React frontend using the React Apollo client, see the [react-example](https://github.com/bocadilloproject/react-example/tree/react-apollo) example project.
  :::

## Project setup

Setting up your project to serve a GraphQL API is as simple as mounting a `TartifletteApp` as a [nested app](/guide/nested-apps.md):

1. Install Tartiflette and `tartiflette-starlette`:

```bash
pip install tartiflette tartiflette-starlette
```

2. Create an ASGI `TartifletteApp` out of your Tartiflette `engine` or `sdl` string (if these concepts sound unfamiliar, see the [Tartiflette documentation](https://tartiflette.io/docs/tutorial/getting-started)):

```python
# myproject/graphql.py
from tartiflette import Engine, Resolver
from tartiflette_starlette import TartifletteApp

@Resolver("Query.hello")
async def hello(parent, args, ctx, info):
    return "Hello, GraphQL!"

engine = Engine("type Query { hello: String }")
graphql = TartifletteApp(engine=engine)
```

3. Mount it as a [nested app](/guide/nested-apps.md):

```python{3,6}
# myproject/app.py
from bocadillo import App
from .graphql import graphql

app = App()
app.mount("/graphql", graphql)
```

3. Serve the app, and make your first query!

```bash
curl -H "Content-Type: application/graphql"  -d '{ hello }' http://localhost:8000
```

```json
{ "data": { "hello": "Hello, GraphQL!" } }
```

🚀

## Interactive GraphiQL client

The GraphiQL client can be enabled using the `graphiql` option to `TartifletteApp`. We recommend using a [setting](/guide/config.md#settings-module) to provision this option:

```python
# myproject/settings.py
GRAPHIQL = config("GRAPHIQL", default=True)
```

```python
# myproject/graphql.py
from . import settings
# ...
graphql = TartifletteApp(engine=engine, graphiql=settings.GRAPHIQL)
```

It will be accessible on the same endpoint than the regular GraphQL API, e.g. `http://localhost:8000/graphql`.

## Building the API

Once you've completed the above steps, you're in Tartiflette territory! Building the GraphQL API is simply a matter of writing queries, resolvers and mutations.

You can learn more about these concepts here:

- [Queries](https://tartiflette.io/docs/tutorial/create-server)
- [Resolvers](https://tartiflette.io/docs/tutorial/write-your-resolvers)
- [Mutations](https://tartiflette.io/docs/tutorial/write-your-mutation-resolvers)

For more information on using `TartifletteApp`, see the [tartiflette-starlette documentation](https://github.com/tartiflette/tartiflette-starlette).
