Event Documentation
====================

You all probably already know that there are several events, internal and from Discord, that you can receive with your
bot. This page will lead you through all dispatched internal events and a few from Discord.



How to listen for events
************************

Generally, you can listen to an event like this:

.. code-block:: python

    import interactions

    bot = interactions.Client(...)

    # possibility 1
    @bot.event
    async def on_(...):
        ...  # do smth

    # possibility 2
    @bot.event(name="on_")
    async def you_are_free_to_name_this_as_you_want(...):
        ... # do smth

    bot.start()


```` represents the Discord event name - but lowercase and any spaces replaced with ``_``.

For example:

* ``READY`` -> ``on_ready``
* ``GUILD MEMBER ADD`` -> ``on_guild_member_add``

``(...)`` represents the different arguments a function takes. Those arguments differ per event.



Now, let us have a look at different events and how they work, starting with internal events.

Internal Events
****************

All events mentioned in this section have the exact naming as they must be put into the function.

There are several different internal events:

    - ``raw_socket_create``
    - ``on_start``
    - ``on_interaction``
    - ``on_command``
    - ``on_component``
    - ``on_autocomplete``
    - ``on_modal``

Lets now have a look at those events in detail:

Event: ``raw_socket_create``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This event fires on any event sent by Discord, including ``Typing Start``  and ``Voice State Update``.
``Hello``, ``Resumed``, ``Reconnect`` and ``Invalid Session`` still will not be dispatched.

The function handling the event should take in one argument, the type of this argument is a ``dict``.

The value of the argument will be the *raw* data sent from Discord, so it is not recommended to use that event
as long as you don't absolutely need it.


Event: ``on_start``
^^^^^^^^^^^^^^^^^^^
This event fires only when the bot is started.

This function takes no arguments.

.. attention::
    Unlike ``on_ready``, this event will never be dispatched more than once.

Event: ``on_interaction``
^^^^^^^^^^^^^^^^^^^^^^^^^^
This event fires on any interaction (commands, components, autocomplete and modals).

The function needs one argument. It will have the type ``CommandContext`` or ``ComponentContext``.

Because you will have to check for everything, from the ``InteractionType`` to any data inside the context, we do not
recommend using this event unless you have experience with it.


Event: ``on_command``
^^^^^^^^^^^^^^^^^^^^^
This event fires on any Application Command (slash command + context menu command) used.

The function takes in one argument of the type ``CommandContext``.

Using this event, you will have to manually check everything, from name to whether the used commands have sub commands,
options or anything else - everything will be in the raw context and you will have to search for it


Event: ``on_component``
^^^^^^^^^^^^^^^^^^^^^^
This event fires on any Component used (for now, those are Buttons and Select Menus).

The function takes in one argument of the type ``ComponentContext``.

Like ``on_command``, you will have to manually check for everything, i.e for custom id and component type.
Also, you will have to look through the argument to find the selected choices, if you have a select menu.


Event: ``on_autocomplete``
^^^^^^^^^^^^^^^^^^^^^^^^^^
This event fires on any autocomplete triggered.

The function takes in one argument of the type ``CommandContext``.

As already in the events above, you will have to get the important values yourself. Those values are here the
autocompleted option and the user input.


Event: ``on_modal``
^^^^^^^^^^^^^^^^^^^
This event fires on every modal that is submitted.

The function takes in one argument of the type ``CommandContext``.

You will have to get all values yourself and check what modal was used when using this event.


Additionally, if you struggle with getting the values, you can check
:ref:`how it is handled internally `.


After this, let us look at events from the Discord API.

Discord API Events
******************

Events in this section do not match the name needed to put into the function. Please check
:ref:`above ` for how to get the correct name.


There are a lot of events dispatched by the Discord API. All of those can be found `here`_.

The events ``HELLO``, ``RESUMED``, ``RECONNECT``, ``INVALID SESSION`` and ``TYPING START`` are not dispatched by the library.

``TYPING START`` will be included in the raw socket create event. You can
also listen for it if you choose to subclass the WebSocketClient

The event ``VOICE STATE UPDATE`` can be only received with the voice :ref:`Extension `.


Let's now have a look at a few events:

Event: ``READY``
^^^^^^^^^^^^^^^^
This event fires whenever ``READY`` is dispatched by Discord. This happens when connecting to the web socket server.

This function takes no arguments.

.. attention::
    Due to the bot reconnecting during runtime, ``on_ready`` will be dispatched multiple times. If you rely on
    ``on_ready`` to do certain things once, check against a global variable as shown below:

    .. code-block:: python

        _ready: bool = False
        bot = interactions.Client(...)

        @bot.event
        async def on_ready():
            global _ready
            if not _ready:
                ... # do stuff
                _ready = True


Events: ``GUILD MEMBER UPDATE`` and ``GUILD MEMBER ADD``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
These events fire whenever a member joins a guild or a member of a guild gets modified.

The function takes in one argument of the type ``GuildMember``.

The argument has the same methods as a normal ``Member`` object, except the methods *do not take in a guild id*.
Please keep that in mind when using this event.


.. _here: https://Discord.com/developers/docs/topics/gateway#commands-and-events-gateway-events
