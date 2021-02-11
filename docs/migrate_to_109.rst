Migrate To 1.0.9
================

1.0.9 Update includes many feature add/rewrite for easier and better usage.
However, due to that, it includes many critical breaking changes.

This page will show how to deal with those changes.

SlashContext.send()
********************

Before:

.. code-block:: python

    await ctx.send(4, content="Hello, World! This is initial message.")
    await ctx.delete()
    await ctx.send(content="This is followup message.")

After:

.. code-block:: python

    await ctx.respond(eat=False)
    msg = await ctx.send("Hello, World! This is initial message.")
    await msg.delete()
    await ctx.send("This is followup message.")
