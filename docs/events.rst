Event Documentation
====================

You all probably already know that there are several events, internal and from discord, that you can receive with your
bot. This page will lead you through all dispatched internal events and a few from discord.



How to listen for events
************************

Generally, you can listen to an event like this:

.. code-block:: python

    import interactions

    bot = interactions.Client(...)

    # possibility 1
    @bot.event
    async def on_<event name>(...):
        ...  # do smth

    # possibility 2
    @bot.event(name="on_<event name>")
    async def you_are_free_to_name_this_as_you_want(...):
        ... # do smth

    bot.start()


``<event name>`` represents the Discord event name - but lowercase and any spaces replaced with ``_``.

For example:

* ``READY`` -> ``on_ready``
* ``GUILD MEMBER ADD`` -> ``on_guild_member_add``

``(...)`` represents the different arguments a function takes. Those arguments differ per event.



Now, lets have a look on different events and how they work, starting with internal events.

Internal Events
****************

All events mentioned in this section have the exact naming as they have to be put into the function.

There are several different internal events:

    - ``raw_socket_create``
    - ``on_interaction``
    - ``on_command``
    - ``on_component``
    - ``on_autocomplete``
    - ``on_modal``

Lets now have a look on those events in detail:

Event: ``raw_socket_create``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This event fires on any event sent by Discord, including ``Typing Start``  and ``Voice State Update``.
``Hello``, ``Resumed``, ``Reconnect`` and ``Invalid Session`` still will not be dispatched.

The function handling the event should take in one argument, the type of this argument is a ``dict``.

The value of the argument will be the *raw* data sent from discord, so it is not recommended to use that event
as long as you dont absolutely need it.


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

Using this event, you will have to manually check everything, from name to whether the used commands has sub commands,
options or anything else - everything will be in the raw context and you will have to search for it


Event: ``on_component``
^^^^^^^^^^^^^^^^^^^^^^
This event fires on any Component used (for now, those are Buttons and Select Menus).

The function takes in one argument of the type ``ComponentContext``.

Like ``on_command``, you will have to manually check for everything, i.e for custom id and component type.
Also you will have to look through the argument to find the selected choices, if you have a select menu.


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
:ref:`how it is handled internally <https://github.com/interactions-py/library/blob/stable/interactions/api/gateway/client.py#L263-L378>`.


After this, lets look at events from the Discord API.

Discord API Events
******************

Events in this section do not match the name needed to put into the function. Please check
:ref:`above <events:How to listen for events>` for how to get the correct name.


There is a lot of events dispatched by the Discord API. All of those can be found
:ref:`here <https://discord.com/developers/docs/topics/gateway#commands-and-events-gateway-events`.

The events ``HELLO``, ``RESUMED``, ``RECONNECT``, ``INVALID SESSION`` and ``TYPING START`` are not dispatched by the library.

``TYPING START`` will be included into the :ref:`raw socket create<events:event-raw-socket-create>` event. You can
also listen for it if you choose to subclass the :ref:`WebSocketClient<Gateway:WebSocketClient>`

The event ``VOICE STATE UPDATE`` can be only received with the voice :ref:`Extension <faq:Extension Libraries>`.


Lets now have a look at a few events:

Event: ``READY``
^^^^^^^^^^^^^^^^^^^
This event fires whenever ``READY`` is dispatched by discord. This happens when connecting to the web socket server.

This function takes no arguments.

.. attention::
    Due to the bot reconnecting during runtime ``on_read`` will be dispatched multiple times. If you rely on
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
