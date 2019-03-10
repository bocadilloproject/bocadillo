# Roadmap

This documents lists some of the key items that will be worked on or integrated into the framework.

As a complement, be sure to read through the [issue board](https://github.com/bocadilloproject/bocadillo/issues).

## Terminology

- _Priority_ is a number between 1 (lowest) and 3 (highest).
- _Time scale_ is short-term (ST, a few weeks), mid-term (MT, a few months), long-term (LT, a year or more).

## Items

### Data and persistance

| Feature                       | Details                                                              | Priority | Time scale |
| ----------------------------- | -------------------------------------------------------------------- | -------- | ---------- |
| Async ORM (extension)         | Integration w/ [Tortoise ORM][tortoise]                              | 1        | MT         |
| Async serializers (extension) | [DRF-inspired][drf-serializers] RESTful (de)serialization/validation | 1        | MT         |

[tortoise]: https://tortoise.github.io
[drf-serializers]: https://www.django-rest-framework.org/api-guide/serializers/

### Real-time

| Feature                      | Details                                    | Priority | Time scale |
| ---------------------------- | ------------------------------------------ | -------- | ---------- |
| Class-based WebSocket views  |                                            | 2        | MT         |
| WebSocket serializers        | WebSocket message serialization/validation | 1        | MT         |
| Queueing/streaming framework | TBD, see [Faust][faust] as an inspiration  | 1        | LT         |

[faust]: https://faust.readthedocs.io

### Security

| Feature        | Details                                                     | Priority | Time scale |
| -------------- | ----------------------------------------------------------- | -------- | ---------- |
| Authentication | Integrate w/ data layer                                     | 3        | MT         |
| Permissions    | TBD                                                         | 3        | MT         |
| TLS            | Managing TLS certificates is a pain, can we make it easier? | 2        | MT         |

### Architecture

| Feature          | Details                                                                                                | Priority | Time scale |
| ---------------- | ------------------------------------------------------------------------------------------------------ | -------- | ---------- |
| Plugin framework | Install and setup third-party plugins through Queso. See [vue-cli][vue-cli-plugins] as an inspiration. | 2        | MT         |

[vue-cli-plugins]: https://cli.vuejs.org/guide/plugins-and-presets.html#plugins

### Tooling

| Feature             | Details                                                     | Priority | Time scale |
| ------------------- | ----------------------------------------------------------- | -------- | ---------- |
| API docs generation | [Swagger][swagger]?                                         | 2        | MT         |
| `new` command       | Interactive initialization of a project w/ plugin selection | 2        | MT         |
| `add` command       | Install and setup a Queso plugin                            | 2        | MT         |

[swagger]: https://swagger.io

### Documentation

| Feature | Details | Priority |
| ------- | ------- | -------- |

