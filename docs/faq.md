# FAQ

## General

### Why does this project even exist?

Bocadillo was born from a desire to make the best elements of popular WSGI frameworks enter the world of asynchronous programming.

Our dream is to create a framework where it is as easy to work with a database as in Django, to build a REST API as in Falcon, and to get started as in Flask — all this while leveraging modern async Python to build concurrent apps that scale and embrace the real-time web.

Bocadillo would probably not exist without [Starlette][starlette] and [Uvicorn][uvicorn], two open source projects that pioneered the world of asynchronous web frameworks and servers.

[starlette]: https://www.starlette.io
[uvicorn]: https://www.uvicorn.org

::: tip MAINTAINER'S NOTE
I've written a blog post called [How I Built A Python Web Framework And Became An Open Source Maintainer](https://blog.florimondmanca.com/how-i-built-a-web-framework-and-became-an-open-source-maintainer).

Some of the facts may be outdated by now, but if you're interested in the more personal story behind Bocadillo or seek tips on how to start your own open source project, I believe you'll enjoy the read.

— [@FlorimondManca](https://twitter.com/FlorimondManca)
:::

### Why "Bocadillo", and how do you pronounce it?

Bocadillo is named after the Spanish word: _bocadillo_.

It is pronounced the Castilian Spanish way: _**bo-kah-DEE-yo**_ (or `/bokaˈðiʝo/` for phonetics enthusiasts).

In Spain, a _bocadillo_ is a sandwich made with baguette or a similar type of bread, and filled with a mix of ingredients including meat, vegetables or even omelette.

Its simplicity and low cost allowed it to thrive, become an iconic piece of Spanish cuisine and take over the world as a fast-and-healthy meal. It is also the name of a Columbian sugar confection also known as Guava jelly.

This name was chosen because it is short, easy to remember, and reminiscent that web frameworks should be fun, easy to use, and allow to build delicious systems from simple ingredients.

This Spanish inspiration also explains our tagline, "A modern Python web framework built with asynchronous _salsa_".

Congrats, you know all of it! 🎉

### Is Bocadillo stable?

Although most of its core architecture and features probably won't change much, Bocadillo is still in its early days and some changes may be brought to the framework if we deem it necessary. This has happened in the past, and may happen again. We will of course follow best practices and resort to a deprecation cycle if the change is too important to be released out of the blue.

### Who uses Bocadillo?

Visionaries, outsiders, and geeks. That's our wildest guess, at least.

As of today, async is very niche in the Python community. Still, we're pretty confident of the value it can bring in terms of performance, scalability and unique features in the realm of web frameworks.

So, if you're using Bocadillo for a cool project or even in production (wow!), show off! We'd love to [hear from you][contact-maintainers].

### What's coming next?

We have tons of ideas on making Bocadillo better. Check out our [GitHub issues](https://github.com/bocadilloproject/bocadillo/issues) for a few hints on what's to expect in the short-to-long term. If you have ideas yourself, be sure to come and discuss them with us, e.g. by <open-issue text="opening an issue on GitHub"/>.

## Design and API

### Why pass the request and response around everywhere?

At the fundamental level, an HTTP server application takes an HTTP request as input and _returns_ an HTTP response. Many frameworks have implemented this style with great success.

In Bocadillo however, you may have noticed that HTTP views don't _return_ a `Response`.

Instead, they are given the `Request` object (nothing outstanding there) _and_ the `Response` object. Inside a view, the response is _mutated_ as seems fit. Why?

This idea was inspired to us by [Falcon's "responders"][falcon-responders]. In Bocadillo, the `Response` object is very much a **response builder** instead of an actual HTTP response. Which attributes were set and methods were called on the builder determines what the HTTP response effectively sent over the wire will contain.

[falcon-responders]: https://falcon.readthedocs.io/en/stable/user/tutorial.html#creating-resources

We cannot state that this is a better approach, but we do find a few interesting benefits in it.

The main benefit is that of providing a **simpler interface** to you, the developer, while making this interface easy to maintain and easy to extend.

For example, instead of dealing with multiple types of responses (such as `PlainTextResponse`, `JSONResponse`, `StreamingResponse`, etc.), you have only one — the response builder.

Lastly, without this approach we probably wouldn't have been able to implement a pleasant enough API for background tasks or streaming responses. In fact, this is true for any feature that relies on using an attribute, a method or a decorator attached to the `Response` object.

### How fast is Bocadillo?

Quite fast, according to [benchmarks]. Optimizing for speed has not been our primary focus so far, but we'll definitely consider improving it further as the project stabilizes.

[benchmarks]: https://github.com/the-benchmarker/web-frameworks

## Going live

### Is Bocadillo production-ready yet?

We wouldn't go as far as saying so. Only experience will tell. However, if you are using Bocadillo in production already, [let us know][contact-maintainers]!

### Does Bocadillo scale?

Yes, it _should_ in many ways.

Bocadillo being an async framework, you get client concurrency for free, which can help increase request throughput in case that your application is IO-intensive.

Plus, by running Bocadillo using a process manager, you can run multiple processes per machine, further increasing the single-machine throughput.

Other than that, a Bocadillo application can be scaled up and out as any other web app.

::: tip
For hints on deploying Bocadillo applications, see our [Deployment](/discussions/deployment.md) guide.
:::

### Do I need to run Bocadillo behind a reverse proxy such as Nginx?

No, you don't _have_ to.

Bocadillo already serves static files efficiently for you using [WhiteNoise](http://whitenoise.evans.io/en/stable/), and if you're using a process manager like Gunicorn you should be just fine.

In our experience, running behind Nginx should be motivated by specific needs.

## Getting in touch

### How can I get help?

We have a [Gitter chat room][gitter] where you can reach out and ask any questions related to installing or using Bocadillo. There are a few community member over there who may be able to help you out. Remember to be nice, polite and respectful. If nobody answers your question, try making it more specific or give it more time; members who can help may be busy.

[gitter]: https://gitter.im/bocadilloproject/bocadillo

### I think I've found a bug! What should I do?

The first step would be to verify it can be reproduced, and then <open-issue text="open an issue on GitHub"/>.

If you're willing to help fix the bug, detailed instructions can be found in our <repo-page to="CONTRIBUTING.md" text="Contributing guide"/>.

::: warning
If the bug is related to security, **do not** publicly reveal the information. We'll need to handle this privately first, so consider [contacting a maintainer][contact-maintainers].
:::

### How can I contact maintainers?

If you've got anything else to tell us, you can reach out on Twitter. Our official account is <twitter-link/>.

[@bocadillopy]: https://twitter.com/bocadillopy
[contact-maintainers]: #how-can-i-contact-maintainers
