.. currentmodule:: interactions

Bot Client
==========

The bot client is the main class every bot developer using this library will work with. This class easily allows
a developer to connect, build commands, and extend off of it.

Client
******

+--------------+--------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+---------------------+
| name         | type                                                               | description                                                                                                                                     | default             |
+==============+====================================================================+=================================================================================================================================================+=====================+
| intents      | :ref:`Intents object <api.models.flags.Intents>`                   | Allows specific control of permissions the application has when connected. In order to use multiple intents, the ``|`` operator is recommended. | ``Intents.DEFAULT`` |
+--------------+--------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+---------------------+
| shards       | list of tuple integers                                             | Dictates and controls the shards that the application connects under.                                                                           | ``[]``              |
+--------------+--------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+---------------------+
| presence     | :ref:`Client Presence object <api.models.presence.ClientPresence>` | Sets an RPC-like presence on the application when connected to the Gateway.                                                                     | ``None``            |
+--------------+--------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+---------------------+
| disable_sync | bool                                                               | Controls whether synchronization in the user-facing API should be automatic or not.                                                             | ``False``           |
+--------------+--------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+---------------------+

.. autoclass:: interactions.client.Client
    :no-undoc-members:
    :private-members:`