import logging
import typing
import discord
from discord.ext import commands
from . import http
from . import model
from .utils import manage_commands
from inspect import iscoroutinefunction


class SlashCommand:
    """
    Slash command extension class.

    :param client: discord.py Client or Bot instance.
    :type client: Union[discord.Client, discord.ext.commands.Bot]
    :param auto_register: Whether to register commands automatically. Default `False`.
    :type auto_register: bool
    :param override_type: Whether to override checking type of the client and try register event.
    :type override_type: bool

    :ivar _discord: Discord client of this client.
    :ivar commands: Dictionary of the registered commands via :func:`.slash` decorator.
    :ivar req: :class:`.http.SlashCommandRequest` of this client.
    :ivar logger: Logger of this client.
    :ivar auto_register: Whether to register commands automatically.
    :ivar has_listener: Whether discord client has listener add function.
    """

    def __init__(self,
                 client: typing.Union[discord.Client, commands.Bot],
                 auto_register: bool = False,
                 override_type: bool = False):
        self._discord = client
        self.commands = {}
        self.subcommands = {}
        self.logger = logging.getLogger("discord_slash")
        self.req = http.SlashCommandRequest(self.logger)
        self.auto_register = auto_register
        if self.auto_register:
            self._discord.loop.create_task(self.register_all_commands())
        if not isinstance(client, commands.Bot) and not isinstance(client,
                                                                   commands.AutoShardedBot) and not override_type:
            self.logger.info("Detected discord.Client! Overriding on_socket_response.")
            self._discord.on_socket_response = self.on_socket_response
            self.has_listener = False
        else:
            self._discord.add_listener(self.on_socket_response)
            self.has_listener = True

    def remove(self):
        """
        Removes :func:`on_socket_response` event listener from discord.py Client.

        .. warning::
            This is deprecated and will be removed soon.

        .. note::
            This only works if it is :class:`discord.ext.commands.Bot` or
            :class:`discord.ext.commands.AutoShardedBot`.
        """
        if not self.has_listener:
            return
        self._discord.remove_listener(self.on_socket_response)

    def get_cog_commands(self, cog: commands.Cog):
        """
        Gets slash command from :class:`discord.ext.commands.Cog`.

        :param cog: Cog that has slash commands.
        :type cog: discord.ext.commands.Cog
        """
        func_list = [getattr(cog, x) for x in dir(cog)]
        res = [x for x in func_list if
               isinstance(x, model.CogCommandObject) or isinstance(x, model.CogSubcommandObject)]
        for x in res:
            x.cog = cog
            if isinstance(x, model.CogCommandObject):
                self.commands[x.name] = x
            else:
                if x.base in self.commands.keys():
                    self.commands[x.base].allowed_guild_ids += x.allowed_guild_ids
                    self.commands[x.base].has_subcommands = True
                else:
                    _cmd = {
                        "func": None,
                        "description": "No description.",
                        "auto_convert": {},
                        "guild_ids": x.allowed_guild_ids,
                        "api_options": [],
                        "has_subcommands": True
                    }
                    self.commands[x.base] = model.CommandObject(x.base, _cmd)
                if x.base not in self.subcommands.keys():
                    self.subcommands[x.base] = {}
                if x.subcommand_group:
                    if x.subcommand_group not in self.subcommands:
                        self.subcommands[x.base][x.subcommand_group] = {}
                    self.subcommands[x.base][x.subcommand_group][x.name] = x
                else:
                    self.subcommands[x.base][x.name] = x

    def remove_cog_commands(self, cog):
        """
        Removes slash command from :class:`discord.ext.commands.Cog`.

        :param cog: Cog that has slash commands.
        :type cog: discord.ext.commands.Cog
        """
        func_list = [getattr(cog, x) for x in dir(cog)]
        res = [x for x in func_list if
               isinstance(x, model.CogCommandObject) or isinstance(x, model.CogSubcommandObject)]
        for x in res:
            if isinstance(x, model.CogCommandObject):
                if x.name not in self.commands.keys():
                    continue # Just in case it is removed due to subcommand.
                if x.name in self.subcommands.keys():
                    self.commands[x.name].func = None
                    continue # Let's remove completely when every subcommand is removed.
                del self.commands[x.name]
            else:
                if x.base not in self.subcommands.keys():
                    continue # Just in case...
                if x.subcommand_group:
                    del self.subcommands[x.base][x.subcommand_group][x.name]
                    if not self.subcommands[x.base][x.subcommand_group]:
                        del self.subcommands[x.base][x.subcommand_group]
                else:
                    del self.subcommands[x.base][x.name]
                if not self.subcommands[x.base]:
                    del self.subcommands[x.base]
                    if x.base in self.commands.keys():
                        if self.commands[x.base].func:
                            self.commands[x.base].has_subcommands = False
                        else:
                            del self.commands[x.base]

    async def register_all_commands(self):
        """
        Registers all slash commands except subcommands to Discord API.\n
        If ``auto_register`` is ``True``, then this will be automatically called.
        """
        await self._discord.wait_until_ready()  # In case commands are still not registered to SlashCommand.
        self.logger.info("Registering commands...")
        for x in self.commands.keys():
            selected = self.commands[x]
            if selected.has_subcommands and not hasattr(selected, "invoke"):
                # Just in case it has subcommands but also has base command.
                # More specific, it will skip if it has subcommands and doesn't have base command coroutine.
                self.logger.debug("Skipping registering subcommands.")
                continue
            if selected.allowed_guild_ids:
                for y in selected.allowed_guild_ids:
                    await manage_commands.add_slash_command(self._discord.user.id,
                                                            self._discord.http.token,
                                                            y,
                                                            x,
                                                            selected.description,
                                                            selected.options)
            else:
                await manage_commands.add_slash_command(self._discord.user.id,
                                                        self._discord.http.token,
                                                        None,
                                                        x,
                                                        selected.description,
                                                        selected.options)
        self.logger.info("Completed registering all commands!")

    def add_slash_command(self,
                          cmd,
                          name: str = None,
                          description: str = None,
                          auto_convert: dict = None,
                          guild_ids: typing.List[int] = None,
                          options: list = None,
                          has_subcommands: bool = False):
        """
        Registers slash command to SlashCommand.

        :param cmd: Command Coroutine.
        :type cmd: Coroutine
        :param name: Name of the slash command. Default name of the coroutine.
        :type name: str
        :param description: Description of the slash command. Default ``None``.
        :type description: str
        :param auto_convert: Dictionary of how to convert option values. Default ``None``.
        :type auto_convert: dict
        :param guild_ids: List of Guild ID of where the command will be used. Default ``None``, which will be global command.
        :type guild_ids: List[int]
        :param options: Options of the slash command.
        :type options: list
        :param has_subcommands: Whether it has subcommand. Default ``False``.
        :type has_subcommands: bool
        """
        name = cmd.__name__ if not name else name
        name = name.lower()
        if name in self.commands.keys():
            tgt = self.subcommands[name]
            has_subcommands = tgt["has_subcommands"]
            guild_ids += tgt["guild_ids"]
        _cmd = {
            "func": cmd,
            "description": description if description else "No description.",
            "auto_convert": auto_convert,
            "guild_ids": guild_ids,
            "api_options": options if options else [],
            "has_subcommands": has_subcommands
        }
        self.commands[name] = model.CommandObject(name, _cmd)
        self.logger.debug(f"Added command `{name}`")

    def add_subcommand(self,
                       cmd,
                       base,
                       subcommand_group=None,
                       name=None,
                       description: str = None,
                       auto_convert: dict = None,
                       guild_ids: typing.List[int] = None):
        """
        Registers subcommand to SlashCommand.

        :param cmd: Subcommand Coroutine.
        :type cmd: Coroutine
        :param base: Name of the base command.
        :type base: str
        :param subcommand_group: Name of the subcommand group, if any. Default ``None`` which represents there is no sub group.
        :type subcommand_group: str
        :param name: Name of the subcommand. Default name of the coroutine.
        :type name: str
        :param description: Description of the subcommand. Default ``None``.
        :type description: str
        :param auto_convert: Dictionary of how to convert option values. Default ``None``.
        :type auto_convert: dict
        :param guild_ids: List of guild ID of where the command will be used. Default ``None``, which will be global command.
        :type guild_ids: List[int]
        """
        base = base.lower()
        subcommand_group = subcommand_group.lower() if subcommand_group else subcommand_group
        name = cmd.__name__ if not name else name
        name = name.lower()
        _cmd = {
            "func": None,
            "description": "No description.",
            "auto_convert": {},
            "guild_ids": guild_ids,
            "api_options": [],
            "has_subcommands": True
        }
        _sub = {
            "func": cmd,
            "name": name,
            "description": description,
            "auto_convert": auto_convert,
            "guild_ids": guild_ids,
        }
        if base not in self.commands.keys():
            self.commands[base] = model.CommandObject(base, _cmd)
        else:
            self.commands[base].has_subcommands = True
            self.commands[base].allowed_guild_ids += guild_ids
        if base not in self.subcommands.keys():
            self.subcommands[base] = {}
        if subcommand_group:
            if subcommand_group not in self.subcommands[base].keys():
                self.subcommands[base][subcommand_group] = {}
            self.subcommands[base][subcommand_group][name] = model.SubcommandObject(_sub, base, name, subcommand_group)
        else:
            self.subcommands[base][name] = model.SubcommandObject(_sub, base, name)
        self.logger.debug(
            f"Added subcommand `{base} {subcommand_group if subcommand_group else ''} {cmd.__name__ if not name else name}`")

    def slash(self,
              *,
              name: str = None,
              description: str = None,
              auto_convert: dict = None,
              guild_id: int = None,
              guild_ids: typing.List[int] = None,
              options: typing.List[dict] = None):
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
        :type name: str
        :param description: Description of the slash command. Default ``None``.
        :type description: str
        :param auto_convert: Dictionary of how to convert option values. Default ``None``.
        :type auto_convert: dict
        :param guild_id: Deprecated. Use ``guild_ids`` instead.
        :type guild_id: int
        :param guild_ids: List of Guild ID of where the command will be used. Default ``None``, which will be global command.
        :type guild_ids: List[int]
        :param options: Options of the slash command. This will affect ``auto_convert`` and command data at Discord API. Default ``None``.
        :type options: List[dict]
        """

        if guild_id:
            self.logger.warning("`guild_id` is deprecated! `Use guild_ids` instead.")
            guild_ids = [guild_id]

        if options:
            # Overrides original auto_convert.
            auto_convert = {}
            for x in options:
                if x["type"] < 3:
                    raise Exception("Please use `subcommand()` decorator for subcommands!")
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
                   guild_ids: typing.List[int] = None):
        """
        Decorator that registers subcommand.\n
        Unlike discord.py, you don't need base command.

        Example:

        .. code-block:: python

            # /group say <str>
            @slash.subcommand(base="group", name="say")
            async def _group_say(ctx, _str):
                await ctx.send(content=_str)

            # /group kick user <user>
            @slash.subcommand(base="group",
                              subcommand_group="kick",
                              name="user",
                              auto_convert={"user": "user"})
            async def _group_kick_user(ctx, user):
                ...

        .. note::
            Unlike normal slash command, this doesn't support ``options`` arg, since it will be very complicated.\n
            Also, subcommands won't be automatically registered to Discord API even if you set ``auto_register`` to ``True``.

        :param base: Name of the base command.
        :type base: str
        :param subcommand_group: Name of the subcommand group, if any. Default ``None`` which represents there is no sub group.
        :type subcommand_group: str
        :param name: Name of the subcommand. Default name of the coroutine.
        :type name: str
        :param description: Description of the subcommand. Default ``None``.
        :type description: str
        :param auto_convert: Dictionary of how to convert option values. Default ``None``.
        :type auto_convert: dict
        :param guild_ids: List of guild ID of where the command will be used. Default ``None``, which will be global command.
        :type guild_ids: List[int]
        """

        def wrapper(cmd):
            self.add_subcommand(cmd, base, subcommand_group, name, description, auto_convert, guild_ids)
            return cmd

        return wrapper

    async def process_options(self, guild: discord.Guild, options: list, auto_convert: dict) -> list:
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
        converters = [
            [guild.get_member, guild.fetch_member],
            guild.get_channel,
            guild.get_role
        ]

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
                if auto_convert[selected["name"]] not in types.keys():
                    to_return.append(selected["value"])
                    continue
                loaded_converter = converters[types[auto_convert[selected["name"]]]]
                if isinstance(loaded_converter, list):
                    cache_first = loaded_converter[0](int(selected["value"]))
                    if cache_first:
                        to_return.append(cache_first)
                        continue
                    loaded_converter = loaded_converter[1]
                try:
                    to_return.append(await loaded_converter(int(selected["value"]))) \
                        if iscoroutinefunction(loaded_converter) else \
                        to_return.append(loaded_converter(int(selected["value"])))
                except (discord.Forbidden, discord.HTTPException):
                    self.logger.warning("Failed fetching user! Passing ID instead.")
                    to_return.append(int(selected["value"]))
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
            ctx = model.SlashContext(self.req, to_use, self._discord, self.logger)
            cmd_name = to_use["data"]["name"]
            if cmd_name not in self.commands.keys() and cmd_name in self.subcommands.keys():
                return await self.handle_subcommand(ctx, to_use)
            selected_cmd = self.commands[to_use["data"]["name"]]
            if selected_cmd.allowed_guild_ids:
                if ctx.guild.id not in selected_cmd.allowed_guild_ids:
                    return
            if selected_cmd.has_subcommands:
                return await self.handle_subcommand(ctx, to_use)
            args = await self.process_options(ctx.guild, to_use["data"]["options"], selected_cmd.auto_convert) \
                if "options" in to_use["data"] else []
            self._discord.dispatch("slash_command", ctx)
            try:
                await selected_cmd.invoke(ctx, *args)
            except Exception as ex:
                await self.on_slash_command_error(ctx, ex)

    async def handle_subcommand(self, ctx: model.SlashContext, data: dict):
        """
        Coroutine for handling subcommand.

        .. warning::
            Do not manually call this.

        :param ctx: :class:`.model.SlashContext` instance.
        :param data: Gateway message.
        """
        if data["data"]["name"] not in self.subcommands.keys():
            return
        base = self.subcommands[data["data"]["name"]]
        sub = data["data"]["options"][0]
        sub_name = sub["name"]
        if sub_name not in base.keys():
            return
        ctx.subcommand = sub_name
        sub_opts = sub["options"] if "options" in sub else []
        for x in sub_opts:
            if "options" in x.keys() or "value" not in x.keys():
                sub_group = x["name"]
                if sub_group not in base[sub_name].keys():
                    return
                ctx.subcommand_group = sub_group
                selected = base[sub_name][sub_group]
                args = await self.process_options(ctx.guild, x["options"], selected.auto_convert) \
                    if "options" in x.keys() else []
                self._discord.dispatch("slash_command", ctx)
                try:
                    await selected.invoke(ctx, *args)
                except Exception as ex:
                    await self.on_slash_command_error(ctx, ex)
                return
        selected = base[sub_name]
        args = await self.process_options(ctx.guild, sub_opts, selected.auto_convert) \
            if "options" in sub.keys() else []
        self._discord.dispatch("slash_command", ctx)
        try:
            await selected.invoke(ctx, *args)
        except Exception as ex:
            await self.on_slash_command_error(ctx, ex)

    async def on_slash_command_error(self, ctx, ex):
        """
        Handles Exception occurred from invoking command.

        Example of adding event:

        .. code-block:: python

            @client.event
            async def on_slash_command_error(ctx, ex):
                ...

        Example of adding listener:

        .. code-block:: python

            @bot.listen()
            async def on_slash_command_error(ctx, ex):
                ...

        :param ctx: Context of the command.
        :type ctx: :class:`.model.SlashContext`
        :param ex: Exception from the command invoke.
        :type ex: Exception
        :return:
        """
        if self.has_listener:
            if self._discord.extra_events.get('on_slash_command_error'):
                self._discord.dispatch("slash_command_error", ctx, ex)
                return
        if hasattr(self._discord, "on_slash_command_error"):
            self._discord.dispatch("slash_command_error", ctx, ex)
            return
        # Prints exception if not overrided or has no listener for error.
        self.logger.exception(f"An exception has occurred while executing command `{ctx.name}`:")
