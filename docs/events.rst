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


`<event name>` represents the Discord event name - but lowercase and any spaces replaced with `_`.

`(...)` represents the different arguments a function takes. Those arguments differ per event.


Now, lets have a look on different events and how they work, starting with internal events.

Internal Events
****************

There are several different internal events:

    - `on_command`
    - `on_component`
    - `on_autocomplete`
    - `on_modal`
    - `on_interaction`
    - `raw_socket_create`




After this, lets look at events from the Discord API.

Discord Events
***************

There is a lot of events dispatched by the Discord API. All of those can be found
:ref:`here <https://discord.com/developers/docs/topics/gateway#commands-and-events-gateway-events`.

The events `Hello`, `Resumed`, `Reconnect`, `Typing Start` and `Invalid Session` are not dispatched by the library.

The event `Voice State Update` can be only received with the voice :ref:`Extension <faq:Extension Libraries>`.
