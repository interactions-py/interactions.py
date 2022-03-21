.. currentmodule:: interactions

Application Commands
====================

This section covers our documentation on data models for application commands.

Application Command object
**************************

This is the main object used for representing an application command from the Discord API.

.. autoclass:: interactions.models.command.ApplicationCommand
    :private-members:
    :members:

Option object 
~~~~~~~~~~~~~

Options are another way of creating “arguments” akin to a text-based command.


.. autoclass:: interactions.models.command.Option
    :private-members:
    :members:

Choice object 
~~~~~~~~~~~~~

A choice is a subset of an option where values have been pre-filled for the end user.

.. autoclass:: interactions.models.command.Choice
    :private-members:
    :members: