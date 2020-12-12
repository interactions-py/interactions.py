import logging
import typing
import discord
from discord.ext import commands
from . import http
from . import model


class SlashCommand:
    """
    Slash command extension class.

    :param client: discord.py Bot class. Although it accepts :class:`discord.Client` at init, using it is not allowed since :class:`discord.Client` doesn't support :func:`add_listener`.
    :type client: Union[discord.Client, discord.ext.commands.Bot]
    """
    def __init__(self,
                 client: typing.Union[discord.Client,
                                      commands.Bot]
                 ):
        if isinstance(client, discord.Client) and not isinstance(client, commands.Bot):
            raise Exception("Currently only commands.Bot is supported.")
        self._discord = client
        self.commands = {}
        self.http = http.SlashCommandRequest()
        self.logger = logging.getLogger("discord_slash")
        self._discord.add_listener(self.on_socket_response)

    def slash(self, name=None):
        """
        Decorator that registers coroutine as a slash command.\n
        1 arg is required for ctx(:func:`discord_slash.model.SlashContext`), and if your slash command has some args, then those args are also required.\n
        All args are passed in order.\n
        Note that Role, User, and Channel types are passed as id, since API doesn't give type of the option for now.

        :param name: Name of the slash command.
        """
        def wrapper(cmd):
            self.commands[cmd.__name__ if not name else name] = cmd
            self.logger.debug(f"Added command `{cmd.__name__ if not name else name}`")
            return cmd
        return wrapper

    def process_options(self, options: dict) -> list:
        """
        Not ready.

        :param options: Dict of options.
        :type options: dict
        :return: list
        :raises: :class:`NotImplementedError` - This is still not implemented.
        """
        raise NotImplementedError

        for x in options:
            pass
        return []

    async def on_socket_response(self, msg):
        """
        This event listener is automatically registered at initialization of this class.\n
        DO NOT MANUALLY REGISTER, OVERRIDE, OR WHATEVER ACTION TO THIS COROUTINE UNLESS YOU KNOW WHAT YOU ARE DOING.

        :param msg: Gateway message.
        """
        if msg["t"] != "INTERACTION_CREATE":
            return
        to_use = msg["d"]
        if to_use["data"]["name"] in self.commands.keys():
            args = [x["value"] for x in to_use["data"]["options"]] if "options" in to_use["data"] else []
            ctx = model.SlashContext(self.http, to_use, self._discord)
            await self.commands[to_use["data"]["name"]](ctx, *args)
