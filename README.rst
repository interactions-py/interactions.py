discord-interactions
====================

**A simple API wrapper for Discord interactions.**

.. image:: https://img.shields.io/pypi/dm/discord-py-slash-command.svg
    :target: https://pypi.python.org/pypi/discord-py-interactions/
    :alt: PyPI Monthly Downloads

.. image:: https://img.shields.io/github/license/goverfl0w/discord-interactions.svg
    :target: https://github.com/goverfl0w/discord-interactions/blob/master/LICENSE
    :alt: License

.. image:: https://img.shields.io/pypi/pyversions/discord-py-interactions.svg
    :target: https://pypi.python.org/pypi/discord-py-interactions/
    :alt: PyPI pyversions

.. image:: https://img.shields.io/pypi/v/discord-py-interactions.svg
    :target: https://pypi.python.org/pypi/discord-py-interactions/
    :alt: PyPI version shields.io

.. image:: https://readthedocs.org/projects/discord-interactions/badge/?version=latest
    :target: http://discord-interactions.readthedocs.io/?badge=latest
    :alt: Documentation Status

.. image:: https://discord.com/api/guilds/789032594456576001/embed.png
    :target: https://discord.gg/KkgMBVuEkx
    :alt: Discord

----

This library specializes in the ability to create and use interactions, a new
implementation to Discord's public API as of December 2020. The strong suits of using
our library are:

- Modern pythonic design that is scalable and modular.
- Asynchronous coroutines and multi-threading capabilities.
- Optimal class object reference with little overhead.
- Easily accessible codebase source.
- Stable/unstable branches for managing module stability when importing.

This means that we're essentially good for:

- Working with application commands.
- Handling contextual data cached from text channels.
- General/basic assignment of guild properties to members.
- Responsive callbacks for buttons and select menus.

And we're not good for:

- Trying to use/connect as a voice client.
- Cooldowns/bucket types.

Installation
============

Use this line to install our library:

.. code-block:: bash

    pip install -U discord-py-interactions

----

- The discord-interactions library is based off of API gateway events. If you are
  looking for a library that is webserver-based, please consider:

  - `dispike <https://github.com/ms7m/dispike>`__
  - `discord-interactions-python
    <https://github.com/discord/discord-interactions-python>`__

- If you are looking for a similar library for other languages, please refer to here:

  - `Discord Developer Documentation
    <https://discord.com/developers/docs/topics/community-resources#interactions>`__
