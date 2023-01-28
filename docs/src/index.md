---
hide:
  - navigation
  - toc
  - feedback
---
!!! danger "Remember"
    These docs are not completed. Please do not panic if something is missing or inaccurate.

We hope this documentation is helpful for you, but don't just ++ctrl+c++ and ++ctrl+v++.

___
Ever since December 2019, this open-source project has become the culmination of dedication and research towards figuring out the best way to bring interactions from Discord to you: we are an easy, simple, scalable and modular library for Discord interactions.

- Tired of using numerous module dependencies for slash commands and buttons?
- Looking for a compatible library that implements all interactions?
- Itching to get your hands on slash commands, but in a simple manner?

Look no more! The goal of this library is to make all three of these questions go from possibilities to trivial matters.

### What can we do?
Our library---inside and out, offers numerous benefits and presents itself as a worthy module in your bot's dependencies:

The base features of our library, built with our API include:

- **Dynamic object data generation**: all event data dispatched from the Gateway is dynamically transformed and generated into two-way serializable JSON objects.
- **Sane rate limiting**: our HTTP client implements pre-emptive rate limit avoidance, so your bot is guaranteed to never hit HTTP ``429``.
- **On-demand cache**: every HTTP request and Gateway event made is cached when needed, so you never have to save information yourself.
- **Simplified data models**: every object presented is accessible as either a raw dictionary/``application/json`` or list of recursive attributes.

Some more unique features that are exclusive to our interactions include:

- **Event-triggered callbacks**: whether a component, application command or interaction response, you'll never need to worry about bridging responses.
- **Dual-way decorator logic**: a decorator can act as both a constructor for an interaction, as well as a callback.
- **API-strict naming**: no more confusion with the naming approach of many libraries; we follow the naming style of interactions from the officially curated Discord Developers documentation.
- **Extensive framework structure**: build your own tools and technologies for our library to develop and integrate community creations.

### What do we not offer?
While we certainly offer a lot of benefits, we unfortunately have our own downsides:
!!! note
    This list is subject to change as time goes on:
        some of these items may be added to the core of the library in the future.

- No native cooldown decorator/method.
- Lack of automatic sharding and voice clients.