.. currentmodule:: interactions

Bot Client
==========

The bot client is largely responsible for simplifying the communication between the bot developer
and API. This section covers documentation for classes, methods and the likes for this.

Client class
************

.. autoclass:: interactions.client.Client
    :private-members:
    :members:

Decorators
**********

Events
~~~~~~

Events are an important aspect of the Discord API, as they provide information based on
a "trigger." These triggers are mostly referred to as :ref:`Gateway events <api.gateway:Events>`.

.. autofunction:: interactions.client.Client.event

Commands
~~~~~~~~

These decorators serve as ways to register partial callback functionality, as well as 
registering a command with the Discord API.

When used for creating a command, these decorators wrap information given into them
as :ref:`Application command objects <models.command.ApplicationCommand>`.

Otherwise, when being used for responding to a command, these decorators parse data through our 
:ref:`context manager <context.CommandContext>` by reading an :ref:`Interaction object <models.misc.Interaction>`.

.. autofunction:: interactions.client.Client.command

.. autofunction:: interactions.client.Client.message_command

.. autofunction:: interactions.client.Client.user_command

Callbacks
~~~~~~~~~

"Callbacks" is our way of defining the methodology behind handling our reaction to something happening.
Similar to events, a callback is a response given to an interaction that is not a command. These decorators
allow bot developers to communicate to the Discord API through other forms of interactions available.

.. autofunction:: interactions.client.Client.component

.. autofunction:: interactions.client.Client.autocomplete

.. autofunction:: interactions.client.Client.modal

Connection options
******************

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
