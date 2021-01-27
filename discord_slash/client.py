import logging
import typing
import discord
from inspect import iscoroutinefunction, getdoc
from discord.ext import commands
from . import http
from . import model
from . import error
from . import context
from .utils import manage_commands


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
    :ivar auto_delete: Whether to delete commands not found in the project automatically.
    :ivar has_listener: Whether discord client has listener add function.
    """

    def __init__(self,
                 client: typing.Union[discord.Client, commands.Bot],
                 auto_register: bool = False,
                 auto_delete: bool = False,
                 override_type: bool = False):
        self._discord = client
        self.commands = {}
        self.subcommands = {}
        self.logger = logging.getLogger("discord_slash")
        self.req = http.SlashCommandRequest(self.logger, self._discord)
        self.auto_register = auto_register
        self.auto_delete = auto_delete

        if self.auto_register and self.auto_delete:
            self._discord.loop.create_task(self.sync_all_commands())
        elif self.auto_register:
            self._discord.loop.create_task(self.register_all_commands())
        elif self.auto_delete:
            self._discord.loop.create_task(self.delete_unused_commands())
        
        if not isinstance(client, commands.Bot) and not isinstance(client,
                                                                   commands.AutoShardedBot) and not override_type:
            self.logger.info("Detected discord.Client! Overriding on_socket_response.")
            self._discord.on_socket_response = self.on_socket_response
            self.has_listener = False
        else:
            self._discord.add_listener(self.on_socket_response)
            self.has_listener = True
            default_add_function = self._discord.add_cog
            def override_add_cog(cog: commands.Cog):
                default_add_function(cog)
                self.get_cog_commands(cog)
            self._discord.add_cog = override_add_cog
            default_remove_function = self._discord.remove_cog
            def override_remove_cog(name: str):
                cog = self._discord.get_cog(name)
                if cog is None:
                    return
                self.remove_cog_commands(cog)
                default_remove_function(name)
            self._discord.remove_cog = override_remove_cog

    def get_cog_commands(self, cog: commands.Cog):
        """
        Gets slash command from :class:`discord.ext.commands.Cog`.

        .. note::
            Since version ``1.0.9``, this gets called automatically during cog initialization.

        :param cog: Cog that has slash commands.
        :type cog: discord.ext.commands.Cog
        """
        if hasattr(cog, '_slash_registered'): # Temporary warning
            return self.logger.warning("Calling get_cog_commands is no longer required "
                                       "to add cog slash commands. Make sure to remove all calls to this function.")
        cog._slash_registered = True # Assuming all went well
        func_list = [getattr(cog, x) for x in dir(cog)]
        res = [x for x in func_list if isinstance(x, (model.CogCommandObject, model.CogSubcommandObject))]
        for x in res:
            x.cog = cog
            if isinstance(x, model.CogCommandObject):
                if x.name in self.commands:
                    raise error.DuplicateCommand(x.name)
                self.commands[x.name] = x
            else:
                if x.base in self.commands:
                    for i in self.commands[x.base].allowed_guild_ids:
                        if i not in x.allowed_guild_ids:
                            x.allowed_guild_ids.append(i)
                    self.commands[x.base].has_subcommands = True
                else:
                    _cmd = {
                        "func": None,
                        "description": x.base_description,
                        "auto_convert": {},
                        "guild_ids": x.allowed_guild_ids,
                        "api_options": [],
                        "has_subcommands": True
                    }
                    self.commands[x.base] = model.CommandObject(x.base, _cmd)
                if x.base not in self.subcommands:
                    self.subcommands[x.base] = {}
                if x.subcommand_group:
                    if x.subcommand_group not in self.subcommands[x.base]:
                        self.subcommands[x.base][x.subcommand_group] = {}
                    if x.name in self.subcommands[x.base][x.subcommand_group]:
                        raise error.DuplicateCommand(f"{x.base} {x.subcommand_group} {x.name}")
                    self.subcommands[x.base][x.subcommand_group][x.name] = x
                else:
                    if x.name in self.subcommands[x.base]:
                        raise error.DuplicateCommand(f"{x.base} {x.name}")
                    self.subcommands[x.base][x.name] = x

    def remove_cog_commands(self, cog):
        """
        Removes slash command from :class:`discord.ext.commands.Cog`.

        .. note::
            Since version ``1.0.9``, this gets called automatically during cog de-initialization.

        :param cog: Cog that has slash commands.
        :type cog: discord.ext.commands.Cog
        """
        if hasattr(cog, '_slash_registered'):
            del cog._slash_registered
        func_list = [getattr(cog, x) for x in dir(cog)]
        res = [x for x in func_list if
               isinstance(x, (model.CogCommandObject, model.CogSubcommandObject))]
        for x in res:
            if isinstance(x, model.CogCommandObject):
                if x.name not in self.commands:
                    continue  # Just in case it is removed due to subcommand.
                if x.name in self.subcommands:
                    self.commands[x.name].func = None
                    continue  # Let's remove completely when every subcommand is removed.
                del self.commands[x.name]
            else:
                if x.base not in self.subcommands:
                    continue  # Just in case...
                if x.subcommand_group:
                    del self.subcommands[x.base][x.subcommand_group][x.name]
                    if not self.subcommands[x.base][x.subcommand_group]:
                        del self.subcommands[x.base][x.subcommand_group]
                else:
                    del self.subcommands[x.base][x.name]
                if not self.subcommands[x.base]:
                    del self.subcommands[x.base]
                    if x.base in self.commands:
                        if self.commands[x.base].func:
                            self.commands[x.base].has_subcommands = False
                        else:
                            del self.commands[x.base]

    async def to_dict(self):
        """
        Converts all commands currently registered to :class:`SlashCommand` to a dictionary.
        Returns a dictionary in the format:

        .. code-block:: python

            {
                "global" : [], # list of global commands
                "guild" : {
                    0000: [] # list of commands in the guild 0000
                }
            }

        Commands are in the format specified by discord `here <https://discord.com/developers/docs/interactions/slash-commands#applicationcommand>`_
        """
        await self._discord.wait_until_ready()  # In case commands are still not registered to SlashCommand.
        commands = {
            "global": [],
            "guild": {}
        }
        for x in self.commands:
            selected = self.commands[x]
            if selected.has_subcommands and selected.func:
                # Registering both subcommand and command with same base name / name
                # will result in only subcommand being registered,
                # so we will warn this at registering subcommands.
                self.logger.warning(f"Detected command name with same subcommand base name! "
                                    f"This command will only have subcommand: {x}")
            
            options = []
            if selected.has_subcommands:
                tgt = self.subcommands[x]
                for y in tgt:
                    sub = tgt[y]
                    if isinstance(sub, model.SubcommandObject):
                        _dict = {
                            "name": sub.name,
                            "description": sub.description or "No Description.",
                            "type": model.SlashCommandOptionType.SUB_COMMAND,
                            "options": sub.options or []
                        }
                        options.append(_dict)
                    else:
                        base_dict = {
                            "name": y,
                            "description": "No Description.",
                            "type": model.SlashCommandOptionType.SUB_COMMAND_GROUP,
                            "options": []
                        }
                        for z in sub:
                            sub_sub = sub[z]
                            _dict = {
                                "name": sub_sub.name,
                                "description": sub_sub.description or "No Description.",
                                "type": model.SlashCommandOptionType.SUB_COMMAND,
                                "options": sub_sub.options or []
                            }
                            base_dict["options"].append(_dict)
                            if sub_sub.subcommand_group_description:
                                base_dict["description"] = sub_sub.subcommand_group_description
                        options.append(base_dict)

            command_dict = {
                "name": x,
                "description": selected.description or "No Description.",
                "options": selected.options if not options else options
            }
            if selected.allowed_guild_ids:
                for y in selected.allowed_guild_ids:
                    try:
                        commands["guild"][y].append(command_dict)
                    except KeyError:
                        commands["guild"][y] = [command_dict]
            else:
                commands["global"].append(command_dict)

        return commands

    async def sync_all_commands(self, delete_from_unused_guilds = True):
        """
        Matches commands registered on Discord to commands registered here.
        Deletes any commands on Discord but not here, and registers any not on Discord.
        This is done with a `put` request.
        If ``auto_register`` and ``auto_delete`` are ``True`` then this will be automatically called.

        :param delete_from_unused_guilds: If the bot should make a request to set no commands for guilds that haven't got any commands regestered in :class:``SlashCommand``
        """
        commands = await self.to_dict()
        self.logger.info("Syncing commands...")
        all_bot_guilds = [guild.id for guild in self._discord.guilds]
        # This is an extremly bad way to do this, because slash cmds can be in guilds the bot isn't in
        # But it's the only way until discord makes an endpoint to request all the guild with cmds registered.

        await self.req.put_slash_commands(slash_commands = commands["global"], guild_id = None)
        
        for guild in commands["guild"]:
            await self.req.put_slash_commands(slash_commands = commands["guild"][guild], guild_id = guild)
            all_bot_guilds.remove(guild)
        if delete_from_unused_guilds:
            for guild in all_bot_guilds:
                await self.req.put_slash_commands(slash_commands=[], guild_id = guild)
        
        self.logger.info("Completed syncing all commands!")

    async def register_all_commands(self):
        """
        Registers all slash commands to Discord API.\n
        If ``auto_register`` is ``True`` and ``auto_delete`` is ``False``, then this will be automatically called.
        """
        self.logger.info("Registering commands...")
        commands = await self.to_dict()
        for command in commands["global"]:
            name = command.pop('name')
            self.logger.debug(f"Registering global command {name}")
            await self.req.add_slash_command(guild_id = None, cmd_name = name, **command)
        
        for guild in commands["guild"]:
            guild_cmds = commands["guild"][guild]
            for command in guild_cmds:
                name = command.pop('name')
                self.logger.debug(f"Registering guild command {name} in guild: {guild}")
                await self.req.add_slash_command(guild_id = guild, cmd_name = name, **command)
        self.logger.info("Completed registering all commands!")

    async def delete_unused_commands(self):
        """
        Unregisters all slash commands which are not used by the project to Discord API.\n
        This might take some time because for every guild the bot is on an API call is made.\n
        If ``auto_delete`` is ``True`` and ``auto_register`` is ``False``, then this will be automatically called.
        """
        await self._discord.wait_until_ready()
        self.logger.info("Deleting unused commands...")
        registered_commands = {}
        global_commands = await self.req.get_all_commands(None)

        for cmd in global_commands:
            registered_commands[cmd["name"]] = {"id": cmd["id"], "guild_id": None}

        for guild in self._discord.guilds:
            # Since we can only get commands per guild we need to loop through every one
            try:
                guild_commands = await self.req.get_all_commands(guild.id)
            except discord.Forbidden:
                # In case a guild has not granted permissions to access commands
                continue

            for cmd in guild_commands:
                registered_commands[cmd["name"]] = {"id": cmd["id"], "guild_id": guild.id}

        for x in registered_commands:
            if x not in self.commands:
                # Delete command if not found locally
                selected = registered_commands[x]
                await self.req.remove_slash_command(selected["guild_id"], selected["id"])

        self.logger.info("Completed deleting unused commands!")

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
        :param description: Description of the slash command. Defaults to command docstring or ``None``.
        :type description: str
        :param auto_convert: Dictionary of how to convert option values. Default ``None``.
        :type auto_convert: dict
        :param guild_ids: List of Guild ID of where the command will be used. Default ``None``, which will be global command.
        :type guild_ids: List[int]
        :param options: Options of the slash command. This will affect ``auto_convert`` and command data at Discord API. Default ``None``.
        :type options: list
        :param has_subcommands: Whether it has subcommand. Default ``False``.
        :type has_subcommands: bool
        """
        name = name or cmd.__name__
        name = name.lower()
        if name in self.commands:
            tgt = self.commands[name]
            if not tgt.has_subcommands:
                raise error.DuplicateCommand(name)
            has_subcommands = tgt.has_subcommands
            for x in tgt.allowed_guild_ids:
                if x not in guild_ids:
                    guild_ids.append(x)

        description = description or getdoc(cmd)

        if options is None:
            options = manage_commands.generate_options(cmd, description)

        if options:
            auto_convert = manage_commands.generate_auto_convert(options)

        _cmd = {
            "func": cmd,
            "description": description,
            "auto_convert": auto_convert,
            "guild_ids": guild_ids,
            "api_options": options,
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
                       base_description: str = None,
                       subcommand_group_description: str = None,
                       auto_convert: dict = None,
                       guild_ids: typing.List[int] = None,
                       options: list = None):
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
        :param description: Description of the subcommand. Defaults to command docstring or ``None``.
        :type description: str
        :param base_description: Description of the base command. Default ``None``.
        :type base_description: str
        :param subcommand_group_description: Description of the subcommand_group. Default ``None``.
        :type subcommand_group_description: str
        :param auto_convert: Dictionary of how to convert option values. Default ``None``.
        :type auto_convert: dict
        :param guild_ids: List of guild ID of where the command will be used. Default ``None``, which will be global command.
        :type guild_ids: List[int]
        :param options: Options of the subcommand. This will affect ``auto_convert`` and command data at Discord API. Default ``None``.
        :type options: list
        """
        base = base.lower()
        subcommand_group = subcommand_group.lower() if subcommand_group else subcommand_group
        name = name or cmd.__name__
        name = name.lower()
        description = description or getdoc(cmd)

        if name in self.commands:
            tgt = self.commands[name]
            for x in tgt.allowed_guild_ids:
                if x not in guild_ids:
                    guild_ids.append(x)

        if options is None:
            options = manage_commands.generate_options(cmd, description)

        if options:
            auto_convert = manage_commands.generate_auto_convert(options)

        _cmd = {
            "func": None,
            "description": base_description,
            "auto_convert": {},
            "guild_ids": guild_ids,
            "api_options": [],
            "has_subcommands": True
        }
        _sub = {
            "func": cmd,
            "name": name,
            "description": description,
            "base_desc": base_description,
            "sub_group_desc": subcommand_group_description,
            "auto_convert": auto_convert,
            "guild_ids": guild_ids,
            "api_options": options
        }
        if base not in self.commands:
            self.commands[base] = model.CommandObject(base, _cmd)
        else:
            self.commands[base].has_subcommands = True
            self.commands[base].allowed_guild_ids = guild_ids
            if self.commands[base].description:
                _cmd["description"] = self.commands[base].description
        if base not in self.subcommands:
            self.subcommands[base] = {}
        if subcommand_group:
            if subcommand_group not in self.subcommands[base]:
                self.subcommands[base][subcommand_group] = {}
            if name in self.subcommands[base][subcommand_group]:
                raise error.DuplicateCommand(f"{base} {subcommand_group} {name}")
            self.subcommands[base][subcommand_group][name] = model.SubcommandObject(_sub, base, name, subcommand_group)
        else:
            if name in self.subcommands[base]:
                raise error.DuplicateCommand(f"{base} {name}")
            self.subcommands[base][name] = model.SubcommandObject(_sub, base, name)
        self.logger.debug(f"Added subcommand `{base} {subcommand_group or ''} {name or cmd.__name__}`")

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
        All args must be passed as keyword-args.

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

            {"option_role": "role",                      # For key put name of the option and for value put type of the option.
             "option_user": SlashCommandOptionType.USER, # Also can use an enumeration member for the type
             "option_user_two": 6,                       # or number
             "option_channel": "CHANNEL"}                # or upper case string.

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
                   base_description: str = None,
                   base_desc: str = None,
                   subcommand_group_description: str = None,
                   sub_group_desc: str = None,
                   auto_convert: dict = None,
                   guild_ids: typing.List[int] = None,
                   options: typing.List[dict] = None):
        """
        Decorator that registers subcommand.\n
        Unlike discord.py, you don't need base command.\n
        All args must be passed as keyword-args.

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

        :param base: Name of the base command.
        :type base: str
        :param subcommand_group: Name of the subcommand group, if any. Default ``None`` which represents there is no sub group.
        :type subcommand_group: str
        :param name: Name of the subcommand. Default name of the coroutine.
        :type name: str
        :param description: Description of the subcommand. Default ``None``.
        :type description: str
        :param base_description: Description of the base command. Default ``None``.
        :type base_description: str
        :param base_desc: Alias of ``base_description``.
        :param subcommand_group_description: Description of the subcommand_group. Default ``None``.
        :type subcommand_group_description: str
        :param sub_group_desc: Alias of ``subcommand_group_description``.
        :param auto_convert: Dictionary of how to convert option values. Default ``None``.
        :type auto_convert: dict
        :param guild_ids: List of guild ID of where the command will be used. Default ``None``, which will be global command.
        :type guild_ids: List[int]
        :param options: Options of the subcommand. This will affect ``auto_convert`` and command data at Discord API. Default ``None``.
        :type options: List[dict]
        """
        base_description = base_description or base_desc
        subcommand_group_description = subcommand_group_description or sub_group_desc

        def wrapper(cmd):
            self.add_subcommand(cmd, base, subcommand_group, name, description, base_description, subcommand_group_description, auto_convert, guild_ids, options)
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

        if not isinstance(guild, discord.Guild):
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
            model.SlashCommandOptionType.USER: 0,
            "6": 0,
            6: 0,
            "channel": 1,
            "CHANNEL": 1,
            model.SlashCommandOptionType.CHANNEL: 1,
            "7": 1,
            7: 1,
            "role": 2,
            "ROLE": 2,
            model.SlashCommandOptionType.ROLE: 2,
            8: 2,
            "8": 2
        }

        to_return = []

        for x in options:
            selected = x
            if selected["name"] in auto_convert:
                if auto_convert[selected["name"]] not in types:
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

        if to_use["data"]["name"] in self.commands:

            ctx = context.SlashContext(self.req, to_use, self._discord, self.logger)
            cmd_name = to_use["data"]["name"]

            if cmd_name not in self.commands and cmd_name in self.subcommands:
                return await self.handle_subcommand(ctx, to_use)

            selected_cmd = self.commands[to_use["data"]["name"]]

            if selected_cmd.allowed_guild_ids:
                guild_id = ctx.guild.id if isinstance(ctx.guild, discord.Guild) else ctx.guild

                if guild_id not in selected_cmd.allowed_guild_ids:
                    return

            if selected_cmd.has_subcommands and not selected_cmd.func:
                return await self.handle_subcommand(ctx, to_use)

            if "options" in to_use["data"]:
                for x in to_use["data"]["options"]:
                    if "value" not in x:
                        return await self.handle_subcommand(ctx, to_use)

            args = await self.process_options(ctx.guild, to_use["data"]["options"], selected_cmd.auto_convert) \
                if "options" in to_use["data"] else []

            self._discord.dispatch("slash_command", ctx)

            try:
                await selected_cmd.invoke(ctx, *args)
            except Exception as ex:
                await self.on_slash_command_error(ctx, ex)

    async def handle_subcommand(self, ctx: context.SlashContext, data: dict):
        """
        Coroutine for handling subcommand.

        .. warning::
            Do not manually call this.

        :param ctx: :class:`.model.SlashContext` instance.
        :param data: Gateway message.
        """
        if data["data"]["name"] not in self.subcommands:
            return
        base = self.subcommands[data["data"]["name"]]
        sub = data["data"]["options"][0]
        sub_name = sub["name"]
        if sub_name not in base:
            return
        ctx.subcommand = sub_name
        sub_opts = sub["options"] if "options" in sub else []
        for x in sub_opts:
            if "options" in x or "value" not in x:
                sub_group = x["name"]
                if sub_group not in base[sub_name]:
                    return
                ctx.subcommand_group = sub_group
                selected = base[sub_name][sub_group]
                args = await self.process_options(ctx.guild, x["options"], selected.auto_convert) \
                    if "options" in x else []
                self._discord.dispatch("slash_command", ctx)
                try:
                    await selected.invoke(ctx, *args)
                except Exception as ex:
                    await self.on_slash_command_error(ctx, ex)
                return
        selected = base[sub_name]
        args = await self.process_options(ctx.guild, sub_opts, selected.auto_convert) \
            if "options" in sub else []
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
