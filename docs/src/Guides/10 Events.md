---
search:
  boost: 3
---

# Events

Events (in interactions.py) are pieces of information that are sent whenever something happens in Discord or in the library itself - this includes channel updates, message sending, the bot starting up, and more.

## Intents

What events you subscribe to are defined at startup by setting your `Intents`.

By default, interactions.py automatically uses every intent but privileged intents (discussed in a bit). This means you're receiving data about *a lot* of events - it's nice to have those intents while starting out, but we heavily encourage narrowing them so that your bot uses less memory and isn't slowed down by processing them.

There are two ways of setting them. We'll use the `GUILDS` and `GUILD_INVITES` intents as an example, but you should decide what intents you need yourself.

=== ":one: Directly through `Intents`"
    ```python
    from interactions import Client, Intents
    bot = Client(intents=Intents.GUILDS | Intents.GUILD_INVITES)
    ```

=== ":two: `Intents.new`"
    ```python
    from interactions import Client, Intents
    bot = Client(intents=Intents.new(guilds=True, guild_invites=True))
    ```

Some intents are deemed to have sensitive content by Discord and so have extra restrictions on them - these are called **privileged intents.** At the time of writing, these include *message content, guild members, and presences.* These require extra steps to enable them for your bot:

1. Go to the [Discord developer portal](https://discord.com/developers/applications/).
2. Select your application.
3. In the "Bot" tab, go to the "Privileged Gateway Intents" category and scroll down to the privileged intents you want.
4. Enable the toggle.
    - **If your bot is verified or in more than 100 servers, you need to apply for the intent through Discord in order to toggle it.** This may take a couple of weeks.

Then, you can specify it in your bot just like the other intents. If you encounter any errors during this process, [referring to the intents page on Discord's documentation](https://discord.com/developers/docs/topics/gateway#gateway-intents) may help.

!!! danger
    `Intents.ALL` is a shortcut provided by interactions.py to enable *every single intent, including privileged intents.* This is very useful while testing bots, **but this shortcut is an incredibly bad idea to use when actually running your bots for use.** As well as adding more strain on the bot (as discussed earlier with normal intents), this is just a bad idea privacy wise: your bot likely does not need to know that much data.

For more information, please visit the API reference about Intents [at this page](/interactions.py/API Reference/API Reference/models/Discord/enums/#interactions.models.discord.enums.Intents).

## Subscribing to Events

After your intents have been properly configured, you can start to listen to events. Say, if you wanted to listen to channels being created in a guild the bot can see, then all you would have to do is this:

```python
from interactions import listen
from interactions.api.events import ChannelCreate

@listen(ChannelCreate)
async def an_event_handler(event: ChannelCreate):
    print(f"Channel created with name: {event.channel.name}")
```

As you can see, the `listen` statement marks a function to receive (or, well, listen/subscribe to) a specific event - we specify which event to receive by passing in the *event object*, which is an object that contains all information about an event. Whenever that events happens in Discord, it triggers our function to run, passing the event object into it. Here, we get the channel that the event contains and send out its name to the terminal.

???+ note "Difference from other Python Discord libraries"
    If you come from some other Python Discord libraries, or even come from older versions of interactions.py, you might have noticed how the above example uses an *event object* - IE a `ChannelCreate` object - instead of passing the associated object with that event - IE a `Channel` (or similar) object - into the function. This is intentional - by using event objects, we have greater control of what information we can give to you.

    For pretty much every event object, the object associated with that event is still there, just as an attribute. Here, the channel is in `event.channel` - you'll usually find the object in other events in a similar format.
    Update events usually use `event.before` and `event.after` too.

While the above is the recommended format for listening to events (as you can be sure that you specified the right event), there are other methods for specifying what event you're listening to:

???+ warning "Event name format for some methods"
    You may notice how some of these methods require the event name to be `all_in_this_case`. The casing itself is called *snake case* - it uses underscores to indicate either a literal space or a gap between words, and exclusively uses lowercase otherwise. To transform an event object, which is in camel case (more specifically, Pascal case), to snake case, first take a look at the letters that are capital, make them lowercase, and add an underscore before those letters *unless it's the first letter of the name of the object*.

    For example, looking at **C**hannel**C**reate, we can see two capital letters. Making them lowercase makes it **c**hannel**c**reate, and then adding an underscore before them makes them **c**hannel**_c**reate (notice how the first letter does *not* have a lowercase before them).

    You *can* add an `on_` prefixed before the modified event name too. For example, you could use both `on_channel_create` and `channel_create`, depending on your preference.

    If you're confused by any of this, stay away from methods that use this type of name formatting.

=== ":one: Type Annotation"
    ```python
    @listen()
    async def an_event_handler(event: ChannelCreate):
        ...
    ```

=== ":two: String in `listen`"
    ```python
    @listen("channel_create")
    async def an_event_handler(event):
        ...
    ```

=== ":three: Function name"
    ```python
    @listen()
    async def channel_create(event):
        ...
    ```

## Other Notes About Events

### No Argument Events

Some events may have no information to pass - the information is the event itself. This happens with some of the internal events - events that are specific to interactions.py, not Discord.

Whenever this happens, you can specify the event to simply not pass anything into the function, as can be seen with the startup event:

```python
from interactions.api.events import Startup

@listen(Startup)
async def startup_func():
    ...
```

If you forget, the library will just pass an empty object to avoid errors.

### Disabling Default Listeners

Some internal events, like `ModalCompletion`, have default listeners that perform niceties like logging the command/interaction logged. You may not want this, however, and may want to completely override this behavior without subclassing `Client`. If so, you can achieve it through `disable_default_listeners`:

```python
from interactions.api.events import ModalCompletion

@listen(ModalCompletion, disable_default_listeners=True)
async def my_modal_completion(event: ModalCompletion):
    print("I now control ModalCompletion!")
```

A lot of times, this behavior is used for custom error tracking. If so, [take a look at the error tracking guide](../25 Error Tracking) for a guide on that.

## Events to Listen To

There are a plethora of events that you can listen to. You can find a list of events that are currently supported through the two links below - every class listened on these two pages are available for you, though be aware that your `Intents` must be set appropriately to receive the event you are looking for.

- [Discord Events](/interactions.py/API Reference/API Reference/events/discord/)
- [Internal Events](/interactions.py/API Reference/API Reference/events/internal/)

### Frequently Used Events

- [Startup](/interactions.py/API Reference/API Reference/events/internal/#interactions.api.events.internal.Startup) is an event, as its name implies, that runs when the bot is first started up - more specifically, it runs when the bot is first ready to do actions. This is a good place to set up tools or libraries that require an asynchronous function.
- [Error](/interactions.py/API Reference/API Reference/events/internal/#interactions.api.events.internal.Error) and its many, *many* subclasses about specific types of errors trigger whenever an error occurs while the bot is running. If you want error *tracking* (IE just logging the errors you get to fix them later on), then [take a look at the error tracking guide](../25 Error Tracking). Otherwise, you can do specific error handling using these events (ideally with `disable_default_listeners` turned on) to provide custom messages for command errors.
- [Component](/interactions.py/API Reference/API Reference/events/internal/#interactions.api.events.internal.Component), [ButtonPressed](/interactions.py/API Reference/API Reference/events/internal/#interactions.api.events.internal.ButtonPressed), [Select](/interactions.py/API Reference/API Reference/events/internal/#interactions.api.events.internal.Select), and [ModalCompletion](/interactions.py/API Reference/API Reference/events/internal/#interactions.api.events.internal.ModalCompletion) may be useful for you if you're trying to respond to component or modal interactions - take a look at the [component guide](../05 Components) or the [modal guide](../06 Modals) for more information.
- [MessageCreate](/interactions.py/API Reference/API Reference/discord/#interactions.api.events.discord.MessageCreate) is used whenever anyone sends a message to a channel the bot can see. This can be useful for automoderation, though note *message content is a privileged intent*, as talked about above. For prefixed/text commands in particular, we already have our own implementation - take a look at them [at this page](../26 Prefixed Commands).
- [GuildJoin](/interactions.py/API Reference/API Reference/events/discord/#interactions.api.events.discord.GuildJoin) and [GuildLeft](/interactions.py/API Reference/API Reference/events/discord/#interactions.api.events.discord.GuildLeft) are, as you can expect, events that are sent whenever the bot joins and leaves a guild. Note that for `GuildJoin`, the event triggers for *every guild on startup* - it's best to have a check to see if the bot is ready through `bot.is_ready` and ignore this event if it isn't.
