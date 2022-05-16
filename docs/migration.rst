Migration
=========

This page aims to serve as a guide towards helping users understand any breaking or otherwise important design choices made
between versions to guide towards easy migration between one another.

4.0.1 → 4.0.2
~~~~~~~~~~~~~~~

The biggest major change between these two versions is the way ``HTTPClient`` and modelled API schema objects are used.
In ``4.0.2``, a new ``_client`` attribute is added in model objects in order to use helper methods. This will not be needed
if you're working with dispatched events from the Gateway, however, manually generating your own model object for use
will need it appended as a key-word argument. The example below shows this change:

.. code-block:: python

    # 4.0.1
    data = await bot.http.get_channel(789032594456576004)
    channel = interactions.Channel(**data)

    # 4.0.2
    ...
    channel = interactions.Channel(**data, _client=bot.http)

This change was added in favor for being able to use endpoints in an abstracted state.

4.0.2 → 4.1.0
~~~~~~~~~~~~~~~

``4.1.0`` introduces numerous breaking changes that affect the bot developers' ability to work with mainly modifying
the way our Gateway processes information, as well as supplying a ``reason`` argument to ``HTTPClient``-based methods.

In this version, you are no longer required to give a ``reason`` for every HTTP request. You can instead send it as an optional,
which will work to keep any existing modifications of our codebase from breaking.

Additionally, modifying the way information is dispatched from the Gateway must be done like this now:

.. code-block:: python

    import interactions

    class ExtendedWebSocketClient(interactions.WebSocketClient):
        def _dispatch_event(self, event: str, data: dict):
            super()._dispatch_event(event, data)

            if event != "TYPING_START" and event == "INTERACTION_CREATE":
                ... # run your special interaction dispatch rules here.

We recommend that working in correspondence with this, you should be making use of our ``interactions.ext`` SDK framework.

A slight, yet another breaking change we made was dundering numerous attributes in our internal models.
You will now need to refer to the client's HTTP object as ``_http`` instead of ``http``. In order to view
the full list of these, we highly encourage you to view the documentation readily available.

The last, and most major change is the introduction of the ``MESSAGE_CONTENT`` privileged intent in the library.
Because of ``4.1.0`` using version 10 of the Discord API, this intent is now required for reading all message
content. In order to make sure your bot works still, you will need to enable this intent in your bot's developer
portal and add the intent to your current intents when connecting:

.. code-block:: python

    from interactions import Client, Intents

    bot = Client("TOKEN", intents=Intents.DEFAULT | Intents.MESSAGE_CONTENT)
