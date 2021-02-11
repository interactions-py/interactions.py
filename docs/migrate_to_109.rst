Migrate To 1.0.9
================

1.0.9 Update includes many feature add/rewrite for easier and better usage.
However, due to that, it includes many critical breaking changes.

This page will show how to deal with those changes.

SlashContext
************

.send()
-------

Before:

.. code-block:: python

    # Case 1
    await ctx.send(4, content="Hello, World! This is initial message.")
    await ctx.delete()
    await ctx.send(content="This is followup message.")

    # Case 2
    await ctx.send(content="This is secret message.", complete_hidden=True)

After:

.. code-block:: python

    # Case 1
    await ctx.respond()
    msg = await ctx.send("Hello, World! This is initial message.")
    await msg.delete()
    await ctx.send("This is followup message.")

    # Case 2
    await ctx.respond(eat=True)
    await ctx.send("This is secret message.", hidden=True)
