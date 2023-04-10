# Creating Context Menus

Context menus are interactions under the hood. Defining them is very similar.
Context menus work off `ctx.target` which contains the object the user interacted with.

You can also define `scopes` and `permissions` for them, just like with interactions.

For more information, please visit the API reference [here](/interactions.py/API Reference/API Reference/models/Internal/application_commands/#interactions.models.internal.application_commands.context_menu).

## Message Context Menus

These open up if you right-click a message and choose `Apps`.

This example repeats the selected message:

```python
@message_context_menu(name="repeat")
async def repeat(ctx: ContextMenuContext):
    message: Message = ctx.target
    await ctx.send(message.content)
```

## User Context Menus

These open up if you right-click a user and choose `Apps`.

This example pings the user:

```python
@user_context_menu(name="ping")
async def ping(ctx: ContextMenuContext):
    member: Member = ctx.target
    await ctx.send(member.mention)
```
??? note
    Unlike Slash command names, context menu command names **can** be uppercase, contain special symbols and spaces.
