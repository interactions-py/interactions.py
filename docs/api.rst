.. currentmodule:: interactions

API Reference
=============

This page outlines the API wrapper of discord-interactions.

.. warning::

    As of the time of this writing, version 4.0 of discord-interactions
    has not yet been released, which this documentation currently reflects.
    The documentation written here is subject to change and is not finalized.

Gateway
*******

.. autoclass:: interactions.api.gateway.Heartbeat
    :members:

.. autoclass:: interactions.api.gateway.WebSocket
    :members:

HTTP
****

.. autoclass:: interactions.api.http.Route
    :members:

.. autoclass:: interactions.api.http.Padlock
    :members:

.. autoclass:: interactions.api.http.Request
    :members:

Cache
*****

.. autoclass:: interactions.api.cache.Item
    :members:

.. autoclass:: interactions.api.cache.Storage
    :members:

.. autoclass:: interactions.api.cache.Cache
    :members:

Exceptions
**********

.. autoclass:: interactions.api.error.ErrorFormatter

.. autoexception:: interactions.api.error.InteractionException

.. autoexception:: interactions.api.error.GatewayException