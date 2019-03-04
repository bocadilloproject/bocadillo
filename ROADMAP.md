# Roadmap

This documents lists the key items that will be worked on or integrated into the framework.

## Terminology

- _Priority_ is a number between 1 (lowest) and 3 (highest).
- _Time scale_ is short-term (ST, a few weeks), mid-term (MT, a few months), long-term (LT, a year or more).

## Items

### Data and persistance

| Feature                       | Details                                                              | Priority | Time scale |
| ----------------------------- | -------------------------------------------------------------------- | -------- | ---------- |
| Async ORM (extension)         | Integration w/ [Tortoise ORM][tortoise]                              | 3        | ST-MT      |
| Async serializers (extension) | [DRF-inspired][drf-serializers] RESTful (de)serialization/validation | 3        | MT         |

### Real-time

| Feature                      | Details                                    | Priority | Time scale |
| ---------------------------- | ------------------------------------------ | -------- | ---------- |
| Server-Sent Events           |                                            | 3        | ST         |
| Class-based WebSocket views  |                                            | 2        | MT         |
| Async serializers            | WebSocket message serialization/validation | 1        | MT         |
| Queueing/streaming framework | TBD, see [Faust][faust] as an inspiration  | 1        | LT         |

### Security

| Feature        | Details                                                     | Priority | Time scale |
| -------------- | ----------------------------------------------------------- | -------- | ---------- |
| Authentication | Integrate w/ data layer                                     | 2        | MT         |
| Permissions    | TBD                                                         | 2        | MT         |
| TLS            | Managing TLS certificates is a pain, can we make it easier? | 2        | MT         |

### Architecture

| Feature                        | Details                                                                                                                      | Priority | Time scale |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- | -------- | ---------- |
| Dependency injection mechanism | Notion of services, type annotations-based API, see [Molten][molten-di]                                                      | 1        | MT         |
| Plugin framework               | Mechanism for installing and setting up third-party plugins through Queso. See [vue-cli][vue-cli-plugins] as an inspiration. | 2        | MT         |

### Tooling

| Feature                                      | Details                                                     | Priority | Time scale |
| -------------------------------------------- | ----------------------------------------------------------- | -------- | ---------- |
| Browsable API + API schema + docs generation | [Swagger][swagger]?                                         | 2        | MT         |
| `new` command                                | Interactive initialization of a project w/ plugin selection | 2        | MT         |
| `add` command                                | Install and setup a Queso plugin                            | 2        | MT         |

### Documentation

| Feature                   | Details                | Priority |
| ------------------------- | ---------------------- | -------- |
| Showcase example projects | Blog, web scraper      | 1        | ST |
| Testing infrastructure    | For HTTP and WebSocket | 3        | ST |

[tortoise]: https://tortoise.github.io
[drf-serializers]: https://www.django-rest-framework.org/api-guide/serializers/
[faust]: https://faust.readthedocs.io
[molten-di]: https://moltenframework.com/guide.html#dependency-injection
[vue-cli-plugins]: https://cli.vuejs.org/guide/plugins-and-presets.html#plugins
[swagger]: https://swagger.io
