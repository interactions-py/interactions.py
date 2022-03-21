Frequently Asked Questions
==========================
Got a question about our library? Well, your answer is probably laying somewhere around here.

.. note::

    This page is maintained by the Helpers of the Discord server,
    and developers at their discretion. For any
    comments, feedback or concerns please consider joining our server
    and bringing it up in our support channels.

discord.py is dead! Will this library die too?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The short answer is: **no**.

The decision to become a standalone library that is now an API wrapper for the Discord API
was made before Danny posted his gist on GitHub about ceasing development of discord.py.
This is the official statement from the library developer regarding this:

.. image:: _static/not_dead.png

Are you going to/will/consider fork(ing) discord.py?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The short answer is: **no**.

The long answer is a list of numerous reasons as to why this decision was made:

* There are/will be numerous forks out there for discord.py, and because of that, we cannot safely guarantee our ability to help users out who may be using their own form of modified code.
* The original purpose of this library was to act as an extension of discord.py, but due to the issue of constantly having to monkeypatch solutions into their codebase to keep our library working introduced extreme technical debt. Forking discord.py and building off of it does not change anything from our issue of avoiding this.
* The goal of this library is to solely implement support and integrate the use of interactions from the Discord API. Making this library unique in a sense that we only do this seemed reasonable and within our margin of standards at the time.
* The message intent will inevitably be forced as a privileged intent in April 2022. The practicality of trying to support message commands will be infeasible since Discord Developers have `already admitted`_ that "not wanting to implement application commands" will not be a valid reason for applying for this privileged intent.
* Forking discord.py would be a massive change to our current codebase, throwing away all of the effort we've put into it so far, and basically just be rewriting how v2.0a was created. That would make it nothing more than discord.py-interactions at that point -- plus, we're already a library that keeps very similar naming conventions as discord.py does, so this is pointless.

Will discord.py be able to work with this library?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The short answer is: **yes.**

However, the term "work" is loosely structured here. Imagine it like taping a hole in the wall instead of repairing the wall.
We're essentially "plastering" support for discord.py instead of doing the surgery on its internal organs to make it work well
with our library. As it currently stands, **interactions.py and discord.py** are API wrappers. You will be able to run code
*alongside* one another, and you will be able to plug in some classes, but the data conversion **must be exact.**

What does that mean? Well, we'll show you:

.. code-block:: python

    import interactions
    from discord.ext import commands

    client = interactions.Client(token="...")
    dpy = commands.Bot(prefix="/")

    @dpy.command()
    async def hello(ctx):
        await ctx.send("Hello from discord.py!")

    @client.command(
        name="test",
        description="this is just a testing command."
    )
    async def test(ctx):
        await ctx.send("Hello from discord-interactions!")

    loop = asyncio.get_event_loop()

    task2 = loop.create_task(dpy.start(token="...", bot=True))
    task1 = loop.create_task(client.ready())

    gathered = asyncio.gather(task1, task2, loop=loop)
    loop.run_until_complete(gathered)

Both of these variables ``interactions`` and ``dpy`` will be able to run in the same established environment, and additionally
will both function properly as their respective libraries intend them to. This implementation uses asyncio.gather to execute
both starts simultaneously as asyncio tasks, and runs them under one singular loop.

Compared to traditional startup commands, ``interactions.ready()`` and ``dpy.start()`` is used instead of
the typical ``interactions.start()`` and ``dpy.run()`` methods because of synchronous/async functions.
``asyncio.gather()`` works with coroutines, hence the transition.

What about the models, though? That's a simple answer:

.. code-block:: python

    import discord
    import interactions

    @dpy.command()
    async def borrowing(ctx, member: interactions.Member):
        await ctx.send(f"Member ID: {member.id}")

    @client.command(...)
    async def second_borrowing(ctx, member: discord.Member):
        await ctx.send(f"Member ID: {member.id}")

Both of these will be able to both run and give their proper value. It is *very* important to note here, though, that you
**must** be returning back the exact same information that our objects depend on. A missing class instance can easily lead to
it breaking, hence the "plastering" that is going on here.

Where should we go with discord.py being gone?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The most *biased* answer would be to, of course, *use interactions.py.* We already offer a lot of the integral API wrapper
aspects as discord.py does, however, we only specialize in interactions. Which means things such as these won't be supported
officially by us (but might be available as 3rd parties):

- Cooldowns
- Message commands
- Voice clients

There are other libraries of course though. As a general rule of thumb, if you're looking to do mainly slash commands and that
tidbit then we highly recommend using our library, especially as **discord-components** merges as of version 4.0. But if you
want something way more open and versatile, then we recommend these sources:

- `Pycord`_ (the most actively maintained).
- `dis-snek`_ (high level, "hackable" API wrapper with ease of modification).
- `nextcord`_ (more abstract and fast approach to the Discord API).

It's personally recommended from the library developer to seek these paths instead of sticking to an older version of a library,
e.g. discord.py 1.7.3 or 2.0.0a as they can eventually become deprecated with more pending changes to the API by Discord engineers.

Why are you not supporting cooldowns?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Cooldowns aren't really an actual feature of the Discord API itself, but rather more of a convienent feature implemented in
discord.py in order to avoid spamming of commands.

**What if people spam slash/sub commands?**

That's the neat part: it's really hard to do that, and most of the time, they won't. Unless they copy the exact string that was
used when you open up the UI element to do it numerous times, most users do and will not be able to know how to do this. However,
if you as a bot developer feel at unease about this, you are more than welcome to implement your own cooldown methods yourself.
Cooldowns were an ultimatum that came as the result of message commands being able to be spammable, and since we won't be supporting
them, there's no feasibility to having them in our library.

Will we not be able to create message commands?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This is a tricky question to really answer. If you want the *technical* answer: you can definitely create them with our library,
however, you'll have to program them in the ``on_message_create`` listener event that we use. This is already something a majority
of discord.py bot developers frown upon doing, so this is at your own risk to code your own command handlers into it. Luckily, you
can take a page out of discord.js' book if you want to do this, since they've never heard of an external command handler framework
before in their entire life.


I'm getting "``AttributeError: HTTPClient not found!``" when I try to execute helper methods!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Probably you are doing something like this:

.. code-block:: python

    channel = interactions.Channel(**await bot.http.get_channel(channel_id))
    await channel.send("...")

And the error occurs in the line where you try to send something. You can fix this easy by adding one argument:

.. code-block:: python

    channel = interactions.Channel(**await bot.http.get_channel(channel_id), _client=bot._http)
    await channel.send("...")

You have to add this extra argument for every object you instantiate by yourself if you want to use it's methods


Context and Messages don't have the ``Channel`` and ``Guild`` attributes! Why?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
At the moment the Discord API does *not* include them into their responses.
You can get those object via the ``get_channel()`` and ``get_guild()`` methods of the Context and Message model.


My question is not answered on here!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Please join our Discord server for any further support regarding our library and/or any integration code depending on it.

* Invite Link: https://discord.gg/KkgMBVuEkx

.. _already admitted: https://gist.github.com/Rapptz/4a2f62751b9600a31a0d3c78100287f1#whats-going-to-happen-to-my-bot
.. _Pycord: https://github.com/Pycord-Development/pycord
.. _dis-snek: https://github.com/Discord-Snake-Pit/Dis-Snek
.. _nextcord: https://github.com/nextcord/nextcord
