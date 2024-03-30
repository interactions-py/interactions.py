<!-- icons start at ~64 px/2 em (66 preferred for 1/3 scaling) and decremented by the specified fractional -->
<!-- logo does not follow this rule -->

> [!WARNING]
> This refresh is currently in development. The source can change at any time given
> without warning. If there is a bug, question or concern, please
> [submit an issue. →](https://github.com/interactions-py/interactions.py/issues)

<div>
   <img align="left" height="80" src="https://github.com/interactions-py/interactions.py/assets/111544899/d733bbfb-ddec-4911-8385-0ef4232aee41" />
   <h1>
      interactions.py<br/>
      <img src="https://img.shields.io/badge/Python-3.10+-1081c1?logo=python" />
      <img src="https://img.shields.io/badge/License-GPL-blue" />
      <img src="https://img.shields.io/pypi/dm/discord-py-slash-command.svg?logo=python&label=Downloads" />
      <img src="https://img.shields.io/badge/Docs-latest-x?logo=readthedocs" />
      <img src="https://img.shields.io/badge/Guides-latest-x?logo=readthedocs" />
      <img src="https://discord.com/api/guilds/789032594456576001/embed.png" />
   </h1>
</div>

**interactions.py** is a fast, robust and simple Python API providing feature-rich language bindings for interacting with Discord.

As our name suggests – we focus on *interactions*, including application commands and components for bot developers. This library is
the culmination of years spent researching, designing and testing for the most intuitive; and practical ways to develop applications with them.

## Design

interactions.py is a relatively new and unique library, focusing on providing the essentials needed for every bot developer, all while
offering more:

<img align="left" height="44" src="https://github.com/interactions-py/interactions.py/assets/111544899/90e92b26-8215-4768-aa0e-eaaa35d43b85" />
<ul><ul>
    <b>Full coverage</b><br/>
    We internally reference all of Discord's resource objects and events with pure Python language bindings and our own abstractions,
    eliminating the need to worry about the newest features missing.
</ul></ul>

<img align="left" height="44" src="https://github.com/interactions-py/interactions.py/assets/111544899/2e579e36-686a-464e-9c59-9bf81f849d00" />
<ul><ul>
    <b>Smart TTL caching</b><br/>
    Every event from a Gateway app connection, as well as application commands, fetching and accessing data to-from the API is cached
    with a <i>time-to-live</i>, emphasising performance and avoiding memory bloat.<br/>
    <a href="">Learn more →</a>
</ul></ul>

<img align="left" height="44" src="https://github.com/interactions-py/interactions.py/assets/111544899/8fe15f19-0c97-4996-ad57-f69601b9c534" />
<ul><ul>
    <b>Modern <i>async</i>/<i>await</i> API</b><br/>
    interactions.py is a concurrency-driven library, encouraging and enabling developers to write fast, non-blocking code that executes
    without limited control flow.
</ul></ul>

<img align="left" height="44" src="https://github.com/interactions-py/interactions.py/assets/111544899/f3e18fe1-851e-4169-baa5-fe6ca7b54224" />
<ul><ul>
    <b>Proper rate limiting</b><br/>
    Applications and bots are capable of sending a large volume of requests that risk being gated-off from the API if/when too many are sent.
    We pre-emptively, exhaustively and routinely check the scope of each route with extra safeguards to avoid rate limits.<br/>
    <a href="">Learn more →</a>
</ul></ul>

<img align="left" height="44" src="https://github.com/interactions-py/interactions.py/assets/111544899/79f95af2-8cb8-4728-970a-bf6b7dc2d92d" />
<ul><ul>
    <b>Out-of-the-box feature parity</b><br/>
    Our library architecture caters similarly to those of others', making it easier for developers to quickly pick up pace and learn the
    workings of interactions.py. Although not recommended, we additionally support usage <i>alongside other libraries</i>.*<br/>
    <a href="">Learn more →</a>
</ul></ul>

<img align="left" height="44" src="https://github.com/interactions-py/interactions.py/assets/111544899/841e84c5-f9d2-4dc6-b08c-edc6d00a7d89" />
<ul><ul>
    <b>Automated synchronisation</b><br/>
    interactions.py takes years of experience learned from trying to synchronise application commands and applies it by using an opt-out
    automation process, internally covered by the client detecting for any; and all changes found between your code, and the API.
</ul></ul>

## Extensibility

interactions.py additionally provides bot developers with many builtin extensions to help simplify and offer more functionality
than what's normally included:

<ul><ul>
    <b>Prefixed commands</b><br/>
    <i>By popular request</i>, we've decided to bring prefixed commands to interactions.py as a <u>builtin, yet separate</u>
    extension for those still wishing to bridge application and text-driven commands together, including <i>hybrid</i>.
</ul></ul>

<ul><ul>
    <b>Debugging</b><br/>
    A fully fledged suite of debugging tools and utilities to help you spend less time debugging, and more time coding.
</ul></ul>

<ul><ul>
    <b>Jurigged</b><br/>
    Hot reloading brought to bot applications, automagically updating your bot without manually reloading extensions, all
    while keeping a persistent connection.
</ul></ul>

<ul><ul>
    <b>Sentry</b><br/>
    Sentry brought to Discord! When a problem or issue is detected with a linked Sentry, all of your bot application's errors
    will be sent over.
</ul></ul>

<ul><ul>
    <b>Console</b><br/>
    We add <code>aiomonitor</code> as a dependency to your project, provided with a CLI and portable web interface.
</ul></ul>

<ul><ul>
    <b>Pagination</b><br/>
    "Pages" or numerous embeds containing data, a web-based UX concept pivoted by the UI of Discord's interaction components.
</ul></ul>

## Getting started

> [!NOTE]
> Installations will be moving *away* from `discord-py-interactions` as our PyPI name in the near-term future.
> We suggest using the new name `interactions-py` for future bot development.

interactions.py can be installed via. the [pip](https://pypi.org/project/pip/) package manager:

```console
$ pip install --upgrade discord-py-interactions
```

Creating a bot connection within your code is straightforward, including the ability to "listen" for Discord events
dispatched by the Gateway:

```python
import interactions

app = interactions.Client()

@interactions.listen()
async def on_startup():
    print("App is ready!")

app.start("token")
```

With **interactions.py**, you can quickly and easily build complex Discord applications with Python. Check out our [guides](https://interactions-py.github.io/interactions.py/Guides/01%20Getting%20Started) for more information, or join our [support server. →](https://discord.gg/interactions)
