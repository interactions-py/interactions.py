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

    :ivar _discord: Discord client of this client.
    :ivar commands: Dictionary of the registered commands via :func:`.slash` decorator.
    :ivar req: :class:`.http.SlashCommandRequest` of this client.
    :ivar logger: Logger of this client.
    """
    def __init__(self,
                 client: typing.Union[discord.Client,
                                      commands.Bot]
                 ):
        if isinstance(client, discord.Client) and not isinstance(client, commands.Bot):
            raise Exception("Currently only commands.Bot is supported.")
        self._discord = client
        self.commands = {}
        self.req = http.SlashCommandRequest()
        self.logger = logging.getLogger("discord_slash")
        self._discord.add_listener(self.on_socket_response)

    def slash(self, name=None, auto_convert: dict = None):
        """
        Decorator that registers coroutine as a slash command.\n
        1 arg is required for ctx(:class:`.model.SlashContext`), and if your slash command has some args, then those args are also required.\n
        All args are passed in order.

        .. note::
            Role, User, and Channel types are passed as id, since API doesn't give type of the option for now.

        .. warning::
            Unlike discord.py's command, ``*args``, keyword-only args, converters, etc. are NOT supported.

        Example:

        .. code-block:: python

            @slash.slash(name="ping")
            async def _slash(ctx): # Normal usage.
                await ctx.send(text=f"Pong! (`{round(bot.latency*1000)}`ms)")


            @slash.slash(name="pick")
            async def _pick(ctx, choice1, choice2): # Command with 1 or more args.
                await ctx.send(text=str(random.choice([choice1, choice2])))

        Example of formatting ``auto_convert``:

        .. code-block:: python

            {"option_role": "role",       # For key put name of the option and for value put type of the option.
             "option_user": 6,            # Also can use number for type
             "option_channel": "CHANNEL"} # and all upper case.

        :param name: Name of the slash command.
        :param auto_convert: Dictionary of how to convert option values.
        :type auto_convert: dict
        """
        def wrapper(cmd):
            self.commands[cmd.__name__ if not name else name] = [cmd, auto_convert]
            self.logger.debug(f"Added command `{cmd.__name__ if not name else name}`")
            return cmd
        return wrapper

    def process_options(self, guild: discord.Guild, options: list, auto_convert: dict) -> list:
        """
        Processes Role, User, and Channel option types to discord.py's models.

        :param guild: Guild of the command message.
        :type guild: discord.Guild
        :param options: Dict of options.
        :type options: list
        :param auto_convert: Dictionary of how to convert option values.
        :type auto_convert: dict
        :return: list
        """
        converters = [guild.get_member, guild.get_role, guild.get_role]
        types = {
            "user": 0,
            "USER": 0,
            6: 0,
            "6": 0,
            "channel": 1,
            "CHANNEL": 1,
            7: 1,
            "7": 1,
            "role": 2,
            "ROLE": 2,
            8: 2,
            "8": 2
        }

        to_return = []

        for x in options:
            selected = x
            if selected["name"] in auto_convert.keys():
                loaded_converter = converters[types[auto_convert[selected["name"]]]]
                to_return.append(loaded_converter(int(selected["value"])))
        return to_return

    async def on_socket_response(self, msg):
        """
        This event listener is automatically registered at initialization of this class.

        .. warning::
            DO NOT MANUALLY REGISTER, OVERRIDE, OR WHATEVER ACTION TO THIS COROUTINE UNLESS YOU KNOW WHAT YOU ARE DOING.

        :param msg: Gateway message.
        """
        if msg["t"] != "INTERACTION_CREATE":
            return
        to_use = msg["d"]
        if to_use["data"]["name"] in self.commands.keys():
            selected_cmd = self.commands[to_use["data"]["name"]]
            ctx = model.SlashContext(self.req, to_use, self._discord)
            args = self.process_options(ctx.guild, to_use["data"]["options"], selected_cmd[1]) if "options" in to_use["data"] else []
            await selected_cmd[0](ctx, *args)
