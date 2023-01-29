# Creating Context Menus

Context menus are interactions under the hood. Defining them is very similar.
Context menus work off `ctx.target` which contains the object the user interacted with.

You can also define `scopes` and `permissions` for them, just like with interactions.

For more information, please visit the API reference [here](/interactions.py/API Reference/API Reference/models/Internal/application_commands/#interactions.models.internal.application_commands.context_menu).

## Message Context Menus

These open up if you right-click a message and choose `Apps`.

This example repeats the selected the message:

```python
@context_menu(name="repeat", context_type=CommandTypes.MESSAGE)
async def repeat(ctx: InteractionContext):
    message: Message = ctx.target
    await ctx.send(message.content)
```

## User Context Menus

These open up if you right-click a user and choose `Apps`.

This example pings the user:

```python
@context_menu(name="ping", context_type=CommandTypes.USER)
async def ping(ctx: InteractionContext):
    member: Member = ctx.target
    await ctx.send(member.mention)
```
??? note
    Command names must be lowercase and can only contain `-` and `_` as special symbols and must not contain spaces.
