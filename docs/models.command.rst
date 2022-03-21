.. currentmodule:: interactions

Application Commands
====================

This section covers our documentation on data models for application commands.

Application Command object
**************************

This is the main class used for representing an application command from the Discord API.

.. autoclass:: interations.models.command.ApplicationCommand
    :private-members:
    :members:

Option object 
~~~~~~~~~~~~~

The option object is another way of creating "arguments" akin to a text-based command,.

.. autoclass:: interations.models.command.Option
    :private-members:
    :members:

Choice object 
~~~~~~~~~~~~~

The choice object is a subset of an option where values have been pre-filled for a user.

.. autoclass:: interations.models.command.Choice
    :private-members:
    :members: