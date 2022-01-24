Migration
=========

This page aims to serve as a guide towards helping users understand any breaking or otherwise important design choices made
between versions to guide towards easy migration between one another.

4.0.1 → 4.0.2
~~~~~~~~~~~~~~~

The biggest major change between these two versions is the way ``HTTPClient`` and modelled API schema objects are used.
In ``4.0.2``, a new ``_state`` attribute is added in model objects in order to use helper methods. This will not be needed
if you're working with dispatched events from the Gateway, however, manually generating your own model object for use
will need it appended as a key-word argument. The example below shows this change:

.. code-block:: python

    # 4.0.1
    data = await bot.http.get_channel(789032594456576004)
    channel = interactions.Channel(**data)

    # 4.0.2
    ...
    channel = interactions.Channel(**data, _state=bot.http)

This change was added in favor for being able to use endpoints in an abstracted state.
