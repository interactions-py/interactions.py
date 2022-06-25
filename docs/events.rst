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

``(...)`` represents the different arguments a function takes. Those arguments differ per event.



Now, lets have a look on different events and how they work, starting with internal events.

Internal Events
****************

There are several different internal events:

    - ``raw_socket_create``
    - ``on_command``
    - ``on_component``
    - ``on_autocomplete``
    - ``on_modal``
    - ``on_interaction``


Event: ``raw_socket_create``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This event fires on any event sent by Discord, including ``Typing Start``  and ``Voice State Update``.
``Hello``, ``Resumed``, ``Reconnect`` and ``Invalid Session`` still will not be dispatched.

The function handling the event should take in one argument, the type of this argument is a ``dict``.

The value of the argument will be the *raw* data sent from discord, so it is not recommended to use that event
as long as you dont absolutely need it.


Event: ``on_command``
^^^^^^^^^^^^^^^^^^^^^
This event fires on any Application Command (slash command + context menu command) used.

The function takes in one argument of the type ``CommandContext``

Using this event, you will have to manually check everything, from name to whether the used commands has sub commands,
options or anything else - everything will be in the raw context and you will have to search for it


Event: ``on_component``
^^^^^^^^^^^^^^^^^^^^^^



After this, lets look at events from the Discord API.

Discord Events
***************

There is a lot of events dispatched by the Discord API. All of those can be found
:ref:``here <https://discord.com/developers/docs/topics/gateway#commands-and-events-gateway-events``.

The events ``Hello``, ``Resumed``, ``Reconnect``, ``Invalid Session`` and ``Typing Start`` are not dispatched by the library.

The event ``Voice State Update`` can be only received with the voice :ref:``Extension <faq:Extension Libraries>``.
