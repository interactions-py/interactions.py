# discord-interactions
<strong>A simple API wrapper for Discord interactions.</strong>
=======
<div align="center">
    <a href="https://pypi.org/project/discord-py-interactions/">
        <img src="https://raw.githubusercontent.com/muqshots/discord-py-interactions/master/.github/banner_transparent.png" alt="discord-py-interactions" height="128">
    </a>
    <h2>Your ultimate Discord interactions library for <a href="https://github.com/Rapptz/discord.py">discord.py</a>.</h2>
</div>

[![PyPI download month](https://img.shields.io/pypi/dm/discord-py-slash-command.svg)](https://pypi.python.org/pypi/discord-py-interactions/)
[![GitHub license](https://img.shields.io/github/license/goverfl0w/discord-interactions.svg)](https://github.com/goverfl0w/discord-interactions/blob/master/LICENSE)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/discord-py-interactions.svg)](https://pypi.python.org/pypi/discord-py-interactions/)
[![PyPI version shields.io](https://img.shields.io/pypi/v/discord-py-interactions.svg)](https://pypi.python.org/pypi/discord-py-interactions/)
[![Documentation Status](https://readthedocs.org/projects/discord-interactions/badge/?version=latest)](http://discord-interactions.readthedocs.io/?badge=latest)
[![Discord](https://img.shields.io/discord/789032594456576001.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://discord.gg/KkgMBVuEkx)

---

This library specializes in the ability to create and use interactions, a new implementation to
Discord's public API as of December 2020. The strongsuits of using our library are:

* Modern pythonic design that is scalable and modular.
* Asynchronous coroutines and multi-threading capabilities.
* Optimal class object reference with little overhead.
* Easily accessible codebase source.
* Stable/unstable branches for managing module stability when importing.

This means that we're essentially good for:

* Working with application commands.
* Handling contextual data cached from text channels.
* General/basic assignment of guild properties to members.
* Responsive callbacks for buttons and select menus.

And we're not good for:

* Trying to use/connect as a voice client.
* Cooldowns/bucket types.

# Installation
Use this line to install our library:
`pip install -U discord-py-interactions`

--------

- The discord-interactions library is based off of API gateway events. If you are looking for a library that is webserver-based, please consider:
    - [dispike](https://github.com/ms7m/dispike)
    - [discord-interactions-python](https://github.com/discord/discord-interactions-python)
- If you are looking for a similar library for other languages, please refer to here:
    - [Discord Developer Documentation](https://discord.com/developers/docs/topics/community-resources#interactions)
