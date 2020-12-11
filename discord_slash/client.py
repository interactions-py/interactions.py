import logging
import typing
import discord
from discord.ext import commands
from . import http
from . import model


class SlashCommand:
    def __init__(self,
                 client: typing.Union[discord.Client,
                                      commands.Bot]
                 ):
        if isinstance(client, discord.Client) and not isinstance(client, commands.Bot):
            raise Exception("Currently only ext.Bot is supported.")
        self._discord = client
        self.commands = {}
        self.http = http.SlashCommandRequest()
        self.logger = logging.getLogger("discord_slash")
        self._discord.add_listener(self.on_socket_response)

    def slash(self, name=None):
        def wrapper(cmd):
            self.commands[cmd.__name__ if not name else name] = cmd
            self.logger.debug(f"Added command `{cmd.__name__ if not name else name}`")
            return cmd
        return wrapper

    async def on_socket_response(self, msg):
        if not msg["t"] == "INTERACTION_CREATE":
            return
        to_use = msg["d"]
        if to_use["data"]["name"] in self.commands.keys():
            args = [x["value"] for x in to_use["data"]["options"]] if "options" in to_use["data"] else []
            ctx = model.SlashContext(self.http, to_use, self._discord)
            await self.commands[to_use["data"]["name"]](ctx, *args)
