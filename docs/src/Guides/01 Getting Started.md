# Introduction

Hi! So you want to make a bot starting from naffing. This guide aims to get you started as fast as possible, for more advanced use-cases check out the other guides.

### Requirements

- [x] Python 3.10 or greater
- [x] Know how to use `pip`
- [x] [A bot account](02 Creating Your Bot.md)
- [ ] An aversion to puns

## Installation Methods

There are two different ways to install this library and create your bot.

=== "Using a Template"

    We created a [cookiecutter template](https://github.com/Discord-Snake-Pit/Bot-Template) which you can use to set up your own bot faster.
    With the template, your code will already have a well-defined structure which will make development easier for you.

    We recommend newer devs to make use of this template.

    ### Template Feature
    - Basic, ready to go bot
    - Implementation of best practises
    - NAFF, and general extensibility
    - Example command, context menu, component, and event
    - Logging to both console and file
    - Pip and poetry config
    - Pre-commit config
    - Dockerfile and pre-made docker-compose

    ### Template Installation
    1. Install cookiecutter - `pip install cookiecutter`
    2. Set up the template - `cookiecutter https://github.com/Discord-Snake-Pit/Bot-Template`

    And that's it!

    More information can be found [here](https://github.com/Discord-Snake-Pit/Bot-Template).


=== "Manual Installation"

    ### Virtual-Environments

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
        python3 -m pip install naff --upgrade
        ```

    === ":material-microsoft-windows: Windows"
        ```shell
        py -3 -m pip install naff --upgrade
        ```

    ### Basic bot

    Now let's get a basic bot going, for your code, you'll want something like this:

    ```python
    from naff import Client, Intents, listen

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
        print(f"message received: {event.message.content}")


    bot.start("Put your token here")
    ```

---

Congratulations! You now have a basic understanding of this library.
If you have any questions check out our other guides, or join the
--8<-- "discord_inv.md"

For more examples, check out the [examples page](/Guides/90 Example)
