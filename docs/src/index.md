---
hide:
  - navigation
  - toc
  - feedback
---
!!! danger "Remember"
    These docs are not completed. Please do not panic if something is missing or inaccurate.

We hope this documentation is helpful for you, but don't just ++ctrl+c++ and ++ctrl+v++.

A highly extensible, easy to use, and feature complete framework for Discord.

interactions.py is the culmination of years of experience with Discord's APIs and bot development. This framework has been built from the ground up with community feedback and suggestions in mind. Our framework provides a modern and intuitive set of language bindings for easy interaction with Discord.

## Key Features
interactions.py offers a wide range of features for building Python-powered Discord bots and web applications alike:

- ✅ 100% coverage of the Discord API

- ✅ Dynamic cache with TTL support

- ✅ Modern and Pythonic API for easy interaction with Discord

- ✅ Proper rate-limit handling

- ✅ Feature parity with most other Discord API wrappers

- ✅ Fully automated command synchronisation

In addition to core functionality, interactions.py provides a range of optional extensions, allowing you to further customize your bot and add new features with ease.

## Extensibility

So the base library doesn't do what you want? No problem! With builtin extensions, you are able to extend the functionality of the library. And if none of those pique your interest, there are a myriad of other extension libraries available.

Just type `bot.load_extension("extension")`

---

### Prefixed Commands

Prefixed commands, message commands, or legacy commands.
Whatever you want to call them, by default the `interactions.py` library will not handle these. But rest assured this extension will get you going

- ✅ Automatic command registration

- ✅ Annotation support

### Debug Ext

A fully featured debug and utilities suite to help you get your bots made

### Jurigged

A hot reloading extension allowing you to automagically update your bot without reboots

### Sentry

Integrates Sentry.io error tracking into your bot with a single line

---

## Where do I start?

Getting started with interactions.py is easy! Simply install it via `pip` and start building your Discord application in Python:

`pip install -U discord-py-interactions`
```python
import interactions

bot = interactions.Client()

@interactions.listen()
async def on_startup():
    print("Bot is ready!")

bot.start("token")
```
