# Events

Events are, in Discord's API, pieces of information that are sent whenever something happens in Discord - this includes channel updates, message sending, and more.

## What Events Can I Get

What events you subscribe to are defined at startup by setting your `Intents`.

By default, interactions.py automatically uses every intent but privileged intents (discussed in a bit). This means you're receiving data about *a lot* of events - it's nice to have those intents while starting out, but we heavily encourage narrowing them so that your bot uses less RAM and isn't slowed down by processing them.

There are two ways of setting them. We'll use the `GUILDS` and `GUILD_INVITES` intents as an example, but you should decide what intents you need yourself.

=== ":one: Directly through `Intents`"
    ```python
    from interactions import Intents
    bot = Client(intents=Intents.GUILDS | Intents.GUILD_INVITES)
    ```

=== ":two: `Intents.new`"
    ```python
    from interactions import Intents
    bot = Client(intents=Intents.new(guilds=True, guild_invites=True))
    ```

Some intents are deemed to have sensitive content by Discord and so have extra restrictions on them - these are called **privileged intents.** As of right now, these include *message content, guild members, and presences.* These require extra steps to enable them for your bot:

1. Go to the [Discord developer portal](<https://discord.com/developers/applications/>).
2. Select your application.
3. In the "Bot" tab, go to the "Privileged Gateway Intents" category and scroll down to the privileged intents you want.
4. Enable the toggle.
    - **If your bot is verified or in more than 100 servers, you need to apply for the intent through Discord in order to toggle it.**

Then, you can specify it in your bot just like the other intents.

!!! danger
    `Intents.ALL` is a shortcut provided by interactions.py to enable *every single intents, including privileged intents.* This is very useful while testing bots, **but this shortcut is an incredibly bad idea to use when actually running your bots for use.** As well as adding more strain on the bot (as discussed earlier with normal intents), this is just a bad idea privacy wise: your bot likely does not need to know that much data.

For more information, please visit the API reference [here](/interactions.py/API Reference/API Reference/models/Discord/enums/#interactions.models.discord.enums.Intents).

## Event Listening

After your intents have been properly configured, you can start to listen to events. Say, if you wanted to listen to channels being created in a guild the bot can see, then all you would have to do is this:

```python
from interactions import listen
from interactions.api.events import ChannelCreate

@listen(ChannelCreate)
async def channel_create_handler(event: ChannelCreate):
    print(f"Channel created with name: {event.channel.name}")
```

As you can see, the `listen` statement marks a function to receieve a specific event - we specify which event to receive by passing in the *event object*, which an object that contains all information about an event. Whenever that events happens in Discord, it triggers our function to run, passing the event object into it. Here, we get the channel that the event contains and send out its name to the terminal.

??? note "Difference from other Python Discord libraries"
    If you come from some other Python Discord libraries, or even come from older versions of interactions.py, you might have noticed how the above example uses an *event object* - IE a `ChannelCreate` object - instead of passing the associated object with that event - IE a `Channel` (or similar) object - into the function. This is intentional - by using event objects, we have greater control of what information we can give to you.

    For pretty much every event object, the object associated with that event is still there, just as an attribute. Here, the channel is in `event.channel` - you'll usually find the object in other events in a similar format.

While the above is the recommended format for listening to events (as you can be sure that you specified the right event), there are other methods for specifying what event you're listening to:

???+ warning "Event name format for some methods"
    You may notice how some of these methods require the event name to be `on_all_in_this_case`. The casing itself is called *snake case* - it uses underscores to indicate either a literal space or a gap between words, and exclusively uses lowercase otherwise. To transform an event object, which is in camel case (more specifically, Pascal case), to snake case, first take a look at the letters that are capital, make them lowercase, and add an underscore before them (unless it's the first letter of the object).

    For example, looking at **C**hannel**C**reate, we can see two capital letters. Making them lowercase makes it **c**hannel**c**reate, and then adding an underscore before them makes them **c**hannel**_c**reate (notice how the first letter does *not* have a lowercase before them).

    **However, there is one more step after this.** The methods that use the snake case spelling *also* require using `on_` before them - for example, our ChannelCreate is `on_channel_create`, not just `channel_create`. This matches the behavior of other Python Discord libraries.

    If you're confused by all of this, stay away from methods that use this type of name formatting.

=== ":one: Type Annotation"
    ```python
    @listen()
    async def channel_create_handler(event: ChannelCreate):
        ...
    ```

=== ":two: String in `listen`"
    ```python
    @listen("on_channel_create")
    async def channel_create_handler(event):
        ...
    ```

=== ":three: Function name"
    ```python
    @listen()
    async def on_channel_create(event):
        ...
    ```

You can find all events and their signatures [here](/interactions.py/API Reference/API Reference/events/discord/). Be aware that your `Intents` must be set to receive the event you are looking for.
