---
search:
  boost: 3
---

# Introduction

Ready to get your Python on and create a Discord bot? This guide's got you covered with installation options and a basic bot code example.

### Requirements

- [x] Python 3.10 or greater
- [x] Know how to use `pip`
- [x] [A bot account](02 Creating Your Bot.md)
- [ ] An aversion to puns

## Installing and Setting up a Bot

### Virtual Environments

We strongly recommend that you make use of Virtual Environments when working on any project.
This means that each project will have its own libraries of any version and does not affect anything else on your system.
Don't worry, this isn't setting up a full-fledged virtual machine, just small python environment.

=== ":material-linux: Linux"
    ```shell
    cd "[your bots directory]"
    python3 -m venv venv
    source venv/bin/activate
    ```

=== ":material-microsoft-windows: Windows"
    ```shell
    cd "[your bots directory]"
    py -3 -m venv venv
    venv/Scripts/activate
    ```

It's that simple, now you're using a virtual environment. If you want to leave the environment just type `deactivate`.
If you want to learn more about the virtual environments, check out [this page](https://docs.python.org/3/tutorial/venv.html)

### Pip install

Now let's get the library installed.

=== ":material-linux: Linux"
    ```shell
    python3 -m pip install discord-py-interactions --upgrade
    ```

=== ":material-microsoft-windows: Windows"
    ```shell
    py -3 -m pip install discord-py-interactions --upgrade
    ```

### Basic bot

!!! note
    This is a very basic bot. For a more detailed example/template bot that demonstrates many parts of interactions.py, see [the boilerplate repository.](https://github.com/interactions-py/boilerplate)

Now let's get a basic bot going, for your code, you'll want something like this:

```python
from interactions import Client, Intents, listen

bot = Client(intents=Intents.DEFAULT)
# intents are what events we want to receive from discord, `DEFAULT` is usually fine

@listen()  # this decorator tells snek that it needs to listen for the corresponding event, and run this coroutine
async def on_ready():
    # This event is called when the bot is ready to respond to commands
    print("Ready")
    print(f"This bot is owned by {bot.owner}")


@listen()
async def on_message_create(event):
    # This event is called when a message is sent in a channel the bot can see
    print(f"message received: {event.message.jump_url}")


bot.start("Put your token here")
```

Congratulations! You now have a basic understanding of this library.
If you have any questions check out our other guides, or join the
--8<-- "discord_inv.md"

For more examples, check out the [examples page](/interactions.py/Guides/90 Example)
