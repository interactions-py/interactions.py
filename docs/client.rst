.. currentmodule:: interactions

Bot Client
==========

The bot client is largely responsible for simplifying the communication between the bot developer
and API. This section covers documentation for classes, methods and the likes for this.

.. autoclass:: interactions.client.Client
    :private-members:

.. autofunction:: interactions.client.Client.event

.. autofunction:: interactions.client.Client.event

Connection options
~~~~~~~~~~~~~~~~~~

+--------------+--------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+---------------------+
| name         | type                                                               | description                                                                                                                                     | default             |
+==============+====================================================================+=================================================================================================================================================+=====================+
| intents      | :ref:`Intents object <api.models.flags:Intents>`                   | Allows specific control of permissions the application has when connected. In order to use multiple intents, the ``|`` operator is recommended. | ``Intents.DEFAULT`` |
+--------------+--------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+---------------------+
| shards       | list of tuple integers                                             | Dictates and controls the shards that the application connects under.                                                                           | ``[]``              |
+--------------+--------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+---------------------+
| presence     | :ref:`Client Presence object <api.models.presence:ClientPresence>` | Sets an RPC-like presence on the application when connected to the Gateway.                                                                     | ``None``            |
+--------------+--------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+---------------------+
| disable_sync | bool                                                               | Controls whether synchronization in the user-facing API should be automatic or not.                                                             | ``False``           |
+--------------+--------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+---------------------+
