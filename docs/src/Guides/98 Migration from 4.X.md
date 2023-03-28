# Migrating from 4.X

Version 5.X (and beyond) is a major rewrite of interactions.py compared to 4.X, though there have been major improvements to compensate for the change. 5.X was designed to be more stable and flexible, solving many of the bugs and UX issues 4.X had while also adding additional features you may like.

**You will need to do some updating and rewriting of your code,** but it's not as daunting as it may seem. We've prlovided this document as a starting point (*though it is not exhaustive*), and we have plenty of guides and documentation to help you learn the other parts of this library. Lastly, our support team is always here to help if you need it [in our Discord server](discord.gg/interactions).

Now, let's get started, shall we?

## Python Version Change

Starting from version 5, **Python 3.10 or higher is now required**, whereas version 4 only needed 3.8+. This is because 5.x incorporates many new and exciting features introduced in more recent versions of Python.

For Windows users, this is usually as simple as downloading 3.10 or higher (ideally the latest version for the most speed and features) and possibly removing the old version if you have no other projects that depend on older versions.

For Linux and MacOS, we recommend using [pyenv](https://github.com/pyenv/pyenv); _pyenv lets you easily switch between multiple versions of Python. It's simple, unobtrusive, and follows the UNIX tradition of single-purpose tools that do one thing well._ We strongly suggest consulting pyenv's guides on installation.

If you prefer not to use pyenv, there are many guides available that can help you safely install a newer version of Python alongside your existing version.

## Slash Commands

Slash commands function differently from v4's commands - it's worth taking a good look at the guide to see [how they work in the library now](../03 Creating Commands).

Big changes include the fact that `@bot.command` (we'll get to extensions later) is now `@interactions.slash_command`, and `CommandContext` is now `SlashContext`. There may be some slight renamings elsewhere too in the decorators itself - it's suggested you look over the options for the new decorator and approiately adapt your code.

Arguably the biggest change involves how v5 handles slash options. v5's primary method relies heavily on decorators to do the heavy lifting, though there are other methods you may prefer - again, consult the guide, as that will tell you every method. A general rule of thumb is that if you did not use the "define options as a list right in the slash command decorator" choice, you will have to make some changes to adjust to the new codebase.
Subcommands also cannot be defined as an option in a command. We encourage you to use a subcommand decorator instead, as seen in the guide.

If you were using some of the more complex features of slash commands in v4, it's important to note: *v5 only runs the subcommand, not the base-command-then-subcommands that you could do with v4.* This was mostly due to the logic being too complex to maintain - it is encouraged that you use checks to either add onto base commands or the subcommands you want to add them to, as will be talked about in an upcoming section. `StopIteration` also doesn't exist in v5 due to this change.

Autocomplete *is* different. v5 encourages you to tie autocompletes to specific commands in a different manner than v4 and uses a special context, [like seen in the guide](../03 Creating Commands/#i-need-more-than-25-choices). There is `interactions.global_autocomplete` too.

Autodeferring is also pretty similar, although there's more control, with options to allow for global autodefers and extension-wide ones.

## Other Types of Interactions (Context Menus, Components, Modals)

These should be a lot more familiar to you - many interactions in v5 that aren't slash commands are similar to v4, minus name changes (largely to the decorators and classes you use). They should still *function* similarly though, but it's never a bad idea to consult the various guides that are on the sidebar to gain a better picture of how they work.

[If you're using context menus](../04 Context Menus) (IE `@bot.user_command` or `@bot.message_command`), note that the decorator you use is slightly different from either of the two older ones. You now use `@context_menu`, and specify the type of context menu through `context_type` - otherwise, it's mostly the same.

There also is no "one decorator for every type of command" - there is no equivalent to `bot.command`, and you will need to use the more narrowly-scoped alternatives. Most interaction commands that aren't slash commands use `InteractionContext` for their context too, so keep that in mind.

[For components](../05 Components) and [modals](../06 Modals): you no longer need to use `ActionRow.new(...)` to make an ActionRow now - you can just use `ActionRow(...)` directly. You also send modals via `ctx.send_modal` now. Finally, text inputs in components (the options for string select menus, and the components for modals) are also `*args` now, instead of being a typical parameter:
```python
import interactions

# in v4:

components = [interactions.TextInput(...), interactions.TextInput(...)]

modal = interactions.Modal(
    title="Application Form",
    custom_id="mod_app_form",
    components=components,
)

# in v5:

components = [interactions.InputText(...), interactions.InputText(...)]

modal = interactions.Modal(
    *components,
    title="Application Form",
    custom_id="mod_app_form",
)
```

Otherwise, beyond renamings, components are largely the same.

# WIP - these next sections are not in order of their final appearance

## Extensions

Extensions have not been changed too much. `await teardown(...)` is now just `drop(...)` (note how drop is *not* async), and you use `bot.load_extension`/`bot.unload_extension` instead of `bot.load`/`bot.unload`.

There is one major difference though isn't fully related to extensions themselves - *you use the same decorator for both commands/events in your main file and commands/events in extensions in v5.* Basically, instead of having `bot.command` and `interactions.extension_command`, you *just* have `interactions.slash_command` (and so on for context menus, events, etc.), which functions seemlessly in both contexts.

Also, you no longer require a `setup` function. They can still be used, but if you have no need for them other than just loading the extension, you can get rid of them if you want.

## Cache and interactions.get

interactions.get is a mistake
todo because im running out of battery—

## asyncio Changes

In recent Python versions, `asyncio` has gone through a major change on how it treats its "loops," the major thing that controls asynchronous programming. Instead of allowing libraries to create and manage their own loops, `asyncio` now encourages (and soon will enforce) users to use one loop managed by `asyncio` itself.

What this means to you is that *the `Client` does not have a loop variable, and no `asyncio` loop exists until the bot is started (if you use `bot.start()`).*

For accessing the loop itself, there is [`asyncio.get_running_loop()`](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.get_running_loop) to, well, get the running loop, though you're probably using the loop to run a task - it's better to use [`asyncio.create_task(...)`](https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task) for that instead if you are.

However, as for the second point... it shouldn't impact most users, but this may if you use `create_task` to run an asynchronous function before the bot starts - *this including loading in an extension that uses it before the bot is properly started.* Both of the above functions will error out if used, so using them isn't an option.

So what do you do? Simple - create the loop "yourself" and use `bot.astart()` instead!

Before:
```python
import interactions

# if there's no loop detected, v4 would create the loop for you at this point
# it also stores the loop in bot._loop
bot = interactions.Client(...)

bot._loop.create_task(some_func())
bot.load("an_ext_that_uses_the_event_loop")

bot.start()
```

After:
```python
import asyncio
import interactions

# no bot._loop, loop also does not exist yet
bot = interactions.Client(...)

async def main():
    # loop now exists, woo!
    asyncio.create_task(some_func())
    bot.load_extension("an_ext_that_uses_the_event_loop")
    await bot.astart()

# a function in asyncio that creates the loop for you and runs
# the function within
asyncio.run(main())
```

It's worth noting that you can continue to use `bot.start()` and not change your code if you never relied on `asyncio` like this.
