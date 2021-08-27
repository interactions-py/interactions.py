.. currentmodule:: interactions.api

API Reference
=============

This page outlines the API wrapper of discord-interactions.

.. note::

    This library uses completely different code that is separate
    and detached from the currently existing codebase of discord.py
    respectively. However, due to the given nature of most Discord
    bot developers who use Python as their main programming language,
    we've catered towards naming everything internally a combination
    of the typical nomenclature of discord.py as well as the Discord-
    documented API.

.. warning::

    As of the time of this writing, version 4.0 of discord-interactions
    has not yet been released, which this documentation currently reflects.
    The documentation written here is subject to change and is not finalized.

Gateway
-------

Heartbeat
~~~~~~~~~

.. attributetable:: Heartbeat

.. autoclass:: Heartbeat
    :members:

WebSocket
~~~~~~~~~

.. attributetable:: WebSocket

.. autoclass:: WebSocket
    :members: