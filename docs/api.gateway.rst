.. currentmodule:: interactions

Gateway
=======

This section covers all of the documentation on the Gateway handler, the main implementation for
communicating back and forth between the Discord API's WebSocket server.

WebSocket Client
****************

This is the main client, responsible for connecting to the WebSocket server and dispatching data
received from it.

.. autoclass:: interactions.api.gateway.WebSocketClient
    :private-members:
    :members:

Heartbeater
~~~~~~~~~~~

The "heartbeater" is an abstracted, private class that is internally used to regulate the connection
between the client and the WebSocket server. Without a heartbeat, you, well... we're human so we know
how that works.

.. autoclass:: interactions.api.gateway._Heartbeat
    :private-members:
    :members:
