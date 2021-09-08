Quickstart
==========

Looking into trying to get started with our library? Well, you've come to the right page then!

.. note::

    This quickstart guide is extremely rough and contains experimental code.
    Do not follow us strictly until v4.0 is released! Everything is subject
    to change in here due to the development of the API wrapper continuously
    being reflected.

Installing
**********

**discord-interactions** is a Python library for the Discord Artificial Programming Interface. (API)
A library in Python has to be installed through the `pip` file. Run this in your terminal/command line
in order to install our library:

``pip install -U discord-interactions``

If you're unable to run it through your terminal/command line, you need to make sure that it's
accessible as an Environment Path. Search more on Google for how to do this.

Minimal Bot
***********

Bots can be a little confusing to create. That's why we've decided to try and make the process
as streamlined as humanly possible, in order for it to be friendlier to understand for our
fellow bot developers. Please note that **a Discord bot should not be your first project if you're
learning how to code**. There are plenty of other projects to consider first before this, as a
Discord bot is not exactly beginner-friendly.

This code block below shows a simple bot being created:

.. code-block:: python

    import interactions

    bot = interactions.Client(token="...")

    @bot.application_command(
        name="test",
        description="this is just a test command.",
        guild_id=1234567890
    )
    async def test(ctx):
        await ctx.send("Hello world!")

    bot.start()

There's quite a lot of things that are going on here, so let's break it down step-by-step:

* ``import interactions`` -- This is the import line. If this returns a ``ModuleNotFoundError``, please look at our `Installing`_ section here.
* ``bot = interactions.Client(token="...")`` -- This is the ``bot`` variable that defines our bot. This basically instantiates the `Client`_ class, which requires a ``token`` keyword-argument to be passed. In order to get a token, please look at the image given below.
* ``@bot.application_command()`` -- This is something known as a *decorator* in Python. This decorator is in charge and responsible of making sure that the Discord API is told about the slash/sub command that you wish to create, and sends an HTTP request correspondingly. Any changes to the information contained in this decorator will be synchronously updated with the API automatically for you.
* ``await ctx.send("Hello world!")`` -- This is what lets us send a "message", or otherwise known as an interaction response back to the Discord API for us. ``ctx`` is abbreviated as the "context" of the command, so numerous fields and attributes such as channels, guilds; and etc. are able to be inputted.
* ``bot.start()`` -- Finally, this is what tells our library to turn your bot from offline to online.

.. image:: _static/client_token.png

And it's really as simple as that! If you would like to learn more about what our library offers, or see
more examples of our code, please be sure to check out our `coding examples`_ page on our docs!

.. _Client: https://discord-interactions.rtfd.io/en/unstable/client.html
.. _Installing: https://discord-interactions.rtfd.io/en/unstable/quickstart.html#installing
.. _coding examples: /#/
