# Localising

So your bot has grown, and now you need to ~~localize~~ localise your bot. Well thank god we support localisation then, huh?

To clarify; localisation is a feature of application commands that discord offers,
this means the same command will have different names and descriptions depending on the user's locale settings.

# How its made:

Let's take this nice and simple `hello` command

```python
import interactions

@interactions.slash_command(name="hello")
async def hello_cmd(ctx: interactions.SlashContext):
    await ctx.send(f"Hello {ctx.author.display_name}")
```
This command was immensely popular, and now we have some 🇫🇷 French users. Wouldn't it be nice if we could speak their language.

```python
import interactions
from interactions import LocalisedName

@interactions.slash_command(name=LocalisedName(english_us="hello", french="salut"))
async def hello_cmd(ctx: interactions.SlashContext):
    await ctx.send(f"Hello {ctx.author.display_name}")
```
All we need to do is set the field to a `Localised` object, and interactions.py and discord wil handle the rest for you.
For extra flavour lets make this command more dynamic.

```python
import interactions
from interactions import LocalisedName

@interactions.slash_command(name=LocalisedName(english_us="hello", french="salut"))
async def hello_cmd(ctx: interactions.SlashContext):
    await ctx.send(f"{ctx.invoked_name} {ctx.author.display_name}")
```
Simply by changing `"hello"` to `ctx.invoked_name` the command will always use whatever the user typed to greet them.
If you want to know what locale the user is in, simply use `ctx.locale`.


This will work for any object with a `name` or `description` field. Simply use `LocalisedDesc` instead for descriptions.
For example, you can localise options, choices, and subcommands.
