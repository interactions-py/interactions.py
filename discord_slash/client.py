import logging
import typing
import discord
from discord.ext import commands
from . import http
from . import model
from .utils import manage_commands


class SlashCommand:
    """
    Slash command extension class.

    :param client: discord.py Client or Bot instance.
    :type client: Union[discord.Client, discord.ext.commands.Bot]
    :param auto_register: Whether to register commands automatically. Default `False`. Currently not implemented.
    :type auto_register: bool
    :param override_type: Whether to override checking type of the client and try register event.
    :type override_type: bool

    :ivar _discord: Discord client of this client.
    :ivar commands: Dictionary of the registered commands via :func:`.slash` decorator.
    :ivar req: :class:`.http.SlashCommandRequest` of this client.
    :ivar logger: Logger of this client.
    :ivar auto_register: Whether to register commands automatically.
    """
    def __init__(self,
                 client: typing.Union[discord.Client, commands.Bot],
                 auto_register: bool = False,
                 override_type: bool = False):
        self._discord = client
        self.commands = {}
        self.subcommands = {}
        self.req = http.SlashCommandRequest()
        self.logger = logging.getLogger("discord_slash")
        self.auto_register = auto_register
        if self.auto_register:
            self.logger.warning("auto_register is NOT implemented! Please manually add commands to Discord API.")
        if not isinstance(client, commands.Bot) and not override_type:
            self.logger.info("Detected discord.Client! Overriding on_socket_response.")
            self._discord.on_socket_response = self.on_socket_response
        else:
            self._discord.add_listener(self.on_socket_response)

    def remove(self):
        self._discord.remove_listener(self.on_socket_response)

    def add_slash_command(self,
                          cmd,
                          name: str = None,
                          description: str = None,
                          auto_convert: dict = None,
                          guild_ids: list = None,
                          options: list = None,
                          has_subcommands: bool = False):
        """
        Registers slash command to SlashCommand.

        :param cmd: Command Coroutine.
        :param name: Name of the slash command. Default name of the coroutine.
        :param description: Description of the slash command. Default ``None``.
        :param auto_convert: Dictionary of how to convert option values. Default ``None``.
        :param guild_ids: List of Guild ID of where the command will be used. Default ``None``, which will be global command.
        :param options: Options of the slash command. This will affect ``auto_convert`` and command data at Discord API. Default ``None``.
        :param has_subcommands: Whether it has subcommand. Default ``False``.
        :return: ``None``
        """
        _cmd = {
            "func": cmd,
            "description": description,
            "auto_convert": auto_convert,
            "guild_ids": guild_ids,
            "api_options": options,
            "has_subcommands": has_subcommands
        }
        self.commands[cmd.__name__ if not name else name] = _cmd
        self.logger.debug(f"Added command `{cmd.__name__ if not name else name}`")

    def add_subcommand(self,
                       cmd,
                       base,
                       subcommand_group=None,
                       name=None,
                       description: str = None,
                       auto_convert: dict = None,
                       guild_ids: list = None):
        """
        Registers subcommand to SlashCommand.

        :param cmd:
        :param base:
        :param subcommand_group:
        :param name:
        :param description:
        :param auto_convert:
        :param guild_ids:
        :return:
        """
        name = cmd.__name__ if not name else name
        _cmd = {
            "guild_ids": guild_ids,
            "has_subcommands": True
        }
        _sub = {
            "func": cmd,
            "name": name,
            "description": description,
            "auto_convert": auto_convert,
            "guild_ids": guild_ids,
        }
        self.commands[base] = _cmd
        if base not in self.subcommands.keys():
            self.subcommands[base] = {}
        if subcommand_group:
            if subcommand_group not in self.subcommands[base].keys():
                self.subcommands[base][subcommand_group] = {}
            self.subcommands[base][subcommand_group][name] = _sub
        else:
            self.subcommands[base][name] = _sub

    def slash(self,
              *,
              name: str = None,
              description: str = None,
              auto_convert: dict = None,
              guild_id: int = None,
              guild_ids: list = None,
              options: list = None):
        """
        Decorator that registers coroutine as a slash command.\n
        All decorator args must be passed as keyword-only args.\n
        1 arg for command coroutine is required for ctx(:class:`.model.SlashContext`),
        and if your slash command has some args, then those args are also required.\n
        All args are passed in order.

        .. note::
            Role, User, and Channel types are passed as id if you don't set ``auto_convert``, since API doesn't give type of the option for now.\n
            Also, if ``options`` is passed, then ``auto_convert`` will be automatically created or overrided.

        .. warning::
            Unlike discord.py's command, ``*args``, keyword-only args, converters, etc. are NOT supported.

        Example:

        .. code-block:: python

            @slash.slash(name="ping")
            async def _slash(ctx): # Normal usage.
                await ctx.send(content=f"Pong! (`{round(bot.latency*1000)}`ms)")


            @slash.slash(name="pick")
            async def _pick(ctx, choice1, choice2): # Command with 1 or more args.
                await ctx.send(content=str(random.choice([choice1, choice2])))

        Example of formatting ``auto_convert``:

        .. code-block:: python

            {"option_role": "role",       # For key put name of the option and for value put type of the option.
             "option_user": 6,            # Also can use number for type
             "option_channel": "CHANNEL"} # and all upper case.

        :param name: Name of the slash command. Default name of the coroutine.
        :param description: Description of the slash command. Default ``None``.
        :param auto_convert: Dictionary of how to convert option values. Default ``None``.
        :param guild_id: Deprecated. Use ``guild_ids`` instead.
        :param guild_ids: Guild ID of where the command will be used. Default ``None``, which will be global command.
        :param options: Options of the slash command. This will affect ``auto_convert`` and command data at Discord API. Default ``None``.
        """

        if guild_id:
            self.logger.warning("`guild_id` is deprecated! `Use guild_ids` instead.")
            guild_ids = [guild_id]

        if options:
            # Overrides original auto_convert.
            auto_convert = {}
            for x in options:
                if x["type"] < 3:
                    raise Exception("Currently subcommand is NOT supported.")
                auto_convert[x["name"]] = x["type"]

        def wrapper(cmd):
            self.add_slash_command(cmd, name, description, auto_convert, guild_ids, options)
            return cmd
        return wrapper

    def subcommand(self,
                   *,
                   base,
                   subcommand_group=None,
                   name=None,
                   description: str = None,
                   auto_convert: dict = None,
                   guild_ids: int = None):
        """
        Decorator that registers subcommand.\n
        Unlike discord.py, you don't need base command.\n
        Not implemented.

        Example:

        .. code-block:: python
            @slash.subcommand(base="group", name="say")
            async def _group_say(ctx, _str):
                await ctx.send(content=_str)

        .. note::
            Unlike normal slash command, this doesn't support ``options`` arg, since it will be very complicated.\n
            Also, subcommands won't be automatically registered to Discord API even if you set ``auto_register`` to ``True``.

        :param base: Name of the base command.
        :param subcommand_group: Name of the subcommand group, if any. Default ``None`` which represents there is no sub group.
        :param name: Name of the subcommand. Default name of the coroutine.
        :param description: Description of the subcommand. Default ``None``.
        :param auto_convert: Dictionary of how to convert option values. Default ``None``.
        :param guild_ids: List of guild ID of where the command will be used. Default ``None``, which will be global command.
        :return:
        """
        raise NotImplementedError
        def wrapper(cmd):
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
        if not guild:
            self.logger.info("This command invoke is missing guild. Skipping option process.")
            return [x["value"] for x in options]
        if not auto_convert:
            return [x["value"] for x in options]
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
            if selected_cmd["guild_ids"]:
                if ctx.guild.id not in selected_cmd["guild_ids"]:
                    return
            if selected_cmd["has_subcommands"]:
                return await self.handle_subcommand(ctx, to_use)
            args = self.process_options(ctx.guild, to_use["data"]["options"], selected_cmd["auto_convert"]) \
                if "options" in to_use["data"] else []
            self.logger.debug(f"Command {to_use['data']['name']} invoked.")
            await selected_cmd["func"](ctx, *args)

    async def handle_subcommand(self, ctx: model.SlashContext, data: dict):
        """
        Coroutine for handling subcommand.
        Not implemented.

        :param ctx:
        :param data:
        """
        pass
