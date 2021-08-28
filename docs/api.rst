.. currentmodule:: interactions

API Reference
=============

This page outlines the API wrapper of discord-interactions.

.. warning::

    As of the time of this writing, version 4.0 of discord-interactions
    has not yet been released, which this documentation currently reflects.
    The documentation written here is subject to change and is not finalized.

Client
******

.. autoclass:: interactions.client.Client
    :members:

Gateway
*******

.. note::

    The documentation given below is for showing how the internal processes
    of the API wrapper function. This code **is not required** to be used 
    for running our library. Please refer to our quickstart and interactions
    pages instead.

Heartbeat
---------

.. autoclass:: interactions.api.gateway.Heartbeat
    :members:

WebSocket
---------

.. autoclass:: interactions.api.gateway.WebSocket
    :members:

HTTP Requests
*************

.. autoclass:: interactions.api.http.Request
    :members:

Exceptions
**********

.. autoexception:: interactions.api.error.ErrorFormatter

.. autoexception:: interactions.api.error.InteractionException

.. autoexception:: interactions.api.error.GatewayException