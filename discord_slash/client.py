import copy
import logging
import typing
from contextlib import suppress
from inspect import iscoroutinefunction, getdoc

import discord
from discord.ext import commands

from . import context
from . import error
from . import http
from . import model
from .utils import manage_commands


class SlashCommand:
    """
    Slash command handler class.

    :param client: discord.py Client or Bot instance.
    :type client: Union[discord.Client, discord.ext.commands.Bot]
    :param sync_commands: Whether to sync commands automatically. Default `False`.
    :type sync_commands: bool
    :param delete_from_unused_guilds: If the bot should make a request to set no commands for guilds that haven't got any commands registered in :class:``SlashCommand``. Default `False`.
    :type delete_from_unused_guilds: bool
    :param sync_on_cog_reload: Whether to sync commands on cog reload. Default `False`.
    :type sync_on_cog_reload: bool
    :param override_type: Whether to override checking type of the client and try register event.
    :type override_type: bool

    .. note::
        If ``sync_on_cog_reload`` is enabled, command syncing will be triggered when :meth:`discord.ext.commands.Bot.reload_extension`
        is triggered.

    :ivar _discord: Discord client of this client.
    :ivar commands: Dictionary of the registered commands via :func:`.slash` decorator.
    :ivar req: :class:`.http.SlashCommandRequest` of this client.
    :ivar logger: Logger of this client.
    :ivar sync_commands: Whether to sync commands automatically.
    :ivar sync_on_cog_reload: Whether to sync commands on cog reload.
    :ivar has_listener: Whether discord client has listener add function.
    """

    def __init__(self,
                 client: typing.Union[discord.Client, commands.Bot],
                 sync_commands: bool = False,
                 delete_from_unused_guilds: bool = False,
                 sync_on_cog_reload: bool = False,
                 override_type: bool = False,
                 application_id: typing.Optional[int] = None):
        self._discord = client
        self.commands = {"global": {}}
        self.subcommands = {"global": {}}
        self.logger = logging.getLogger("discord_slash")
        self.req = http.SlashCommandRequest(self.logger, self._discord, application_id)
        self.sync_commands = sync_commands
        self.sync_on_cog_reload = sync_on_cog_reload

        if self.sync_commands:
            self._discord.loop.create_task(self.sync_all_commands(delete_from_unused_guilds))

        if not isinstance(client, commands.Bot) and not isinstance(client,
                                                                   commands.AutoShardedBot) and not override_type:
            self.logger.warning(
                "Detected discord.Client! It is highly recommended to use `commands.Bot`. Do not add any `on_socket_response` event.")
            self._discord.on_socket_response = self.on_socket_response
            self.has_listener = False
        else:
            if not hasattr(self._discord, 'slash'):
                self._discord.slash = self
            else:
                raise error.DuplicateSlashClient("You can't have duplicate SlashCommand instances!")

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

            if self.sync_on_cog_reload:
                orig_reload = self._discord.reload_extension

                def override_reload_extension(*args):
                    orig_reload(*args)
                    self._discord.loop.create_task(self.sync_all_commands(delete_from_unused_guilds))

                self._discord.reload_extension = override_reload_extension

    def get_cog_commands(self, cog: commands.Cog):
        """
        Gets slash command from :class:`discord.ext.commands.Cog`.

        .. note::
            Since version ``1.0.9``, this gets called automatically during cog initialization.

        :param cog: Cog that has slash commands.
        :type cog: discord.ext.commands.Cog
        """
        if hasattr(cog, '_slash_registered'):  # Temporary warning
            return self.logger.warning("Calling get_cog_commands is no longer required "
                                       "to add cog slash commands. Make sure to remove all calls to this function.")
        cog._slash_registered = True  # Assuming all went well
        func_list = [getattr(cog, x) for x in dir(cog)]
        res = [x for x in func_list if isinstance(x, (model.CogCommandObject, model.CogSubcommandObject))]
        for cmd_obj in res:
            guild_ids = cmd_obj.allowed_guild_ids if cmd_obj.allowed_guild_ids else ["global"]
            for guild in guild_ids:
                # make sure guild reference exists in command dicts
                if guild not in self.commands:
                    self.commands[guild] = {}
                if guild not in self.subcommands:
                    self.commands[guild] = {}

                cmd_obj.cog = cog
                if isinstance(cmd_obj, model.CogCommandObject):
                    if cmd_obj.name in self.commands[guild]:
                        raise error.DuplicateCommand(cmd_obj.name)
                    self.commands[guild][cmd_obj.name] = cmd_obj
                else:
                    if cmd_obj.base in self.commands[guild]:
                        for i in cmd_obj.allowed_guild_ids:
                            if i not in self.commands[guild][cmd_obj.base].allowed_guild_ids:
                                self.commands[guild][cmd_obj.base].allowed_guild_ids.append(i)
                        self.commands[guild][cmd_obj.base].has_subcommands = True
                    else:
                        _cmd = {
                            "func": None,
                            "description": cmd_obj.base_description,
                            "auto_convert": {},
                            "guild_ids": cmd_obj.allowed_guild_ids.copy(),
                            "api_options": [],
                            "has_subcommands": True,
                            "connector": {}
                        }
                        self.commands[guild][cmd_obj.base] = model.CommandObject(cmd_obj.base, _cmd)
                    if cmd_obj.base not in self.subcommands[guild]:
                        self.subcommands[guild][cmd_obj.base] = {}
                    if cmd_obj.subcommand_group:
                        if cmd_obj.subcommand_group not in self.subcommands[guild][cmd_obj.base]:
                            self.subcommands[guild][cmd_obj.base][cmd_obj.subcommand_group] = {}
                        if cmd_obj.name in self.subcommands[guild][cmd_obj.base][cmd_obj.subcommand_group]:
                            raise error.DuplicateCommand(f"{cmd_obj.base} {cmd_obj.subcommand_group} {cmd_obj.name}")
                        self.subcommands[guild][cmd_obj.base][cmd_obj.subcommand_group][cmd_obj.name] = cmd_obj
                    else:
                        if cmd_obj.name in self.subcommands[guild][cmd_obj.base]:
                            raise error.DuplicateCommand(f"{cmd_obj.base} {cmd_obj.name}")
                        self.subcommands[guild][cmd_obj.base][cmd_obj.name] = cmd_obj

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
        for cmd_obj in res:
            if isinstance(cmd_obj, model.CogCommandObject):
                guild_ids = cmd_obj.allowed_guild_ids if cmd_obj.allowed_guild_ids else ["global"]
                for guild in guild_ids:
                    if cmd_obj.name not in self.commands[guild]:
                        continue  # Just in case it is removed due to subcommand.
                    if cmd_obj.name in self.subcommands[guild]:
                        self.commands[guild][cmd_obj.name].func = None
                        continue  # Let's remove completely when every subcommand is removed.
                    del self.commands[guild][cmd_obj.name]
            else:
                for guild in self.subcommands:
                    if cmd_obj.base not in self.subcommands[guild]:
                        continue  # Just in case...
                    if cmd_obj.subcommand_group:
                        del self.subcommands[guild][cmd_obj.base][cmd_obj.subcommand_group][cmd_obj.name]
                        if not self.subcommands[guild][cmd_obj.base][cmd_obj.subcommand_group]:
                            del self.subcommands[guild][cmd_obj.base][cmd_obj.subcommand_group]
                    else:
                        del self.subcommands[guild][cmd_obj.base][cmd_obj.name]
                    if not self.subcommands[guild][cmd_obj.base]:
                        del self.subcommands[guild][cmd_obj.base]
                        if cmd_obj.base in self.commands[guild]:
                            if self.commands[guild][cmd_obj.base].func:
                                self.commands[guild][cmd_obj.base].has_subcommands = False
                            else:
                                del self.commands[guild][cmd_obj.base]

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

        output = {}
        cmds = {
            "global": [],
            "guild": {x: [] for x in self.commands.keys() if x != "global"}
        }
        for guild in self.commands:
            for command in self.commands[guild].values():
                command_dict = {
                    "name": command.name,
                    "description": command.description or "No Description",
                    "options": copy.copy(command.options) or []
                }
                if guild not in output:
                    output[guild] = {}
                output[guild][command.name] = copy.deepcopy(command_dict)

        # Separated normal command add and subcommand add not to
        # merge subcommands to one. More info at Issue #88
        # https://github.com/eunwoo1104/discord-py-slash-command/issues/88

        for guild in self.commands:
            for command_name in self.commands[guild]:
                if not self.commands[guild][command_name].has_subcommands:
                    continue
                subcommand_object = self.subcommands[guild][command_name]
                for subcommand_name in subcommand_object:
                    sub = subcommand_object[subcommand_name]
                    if isinstance(sub, model.SubcommandObject):
                        _dict = {
                            "name": sub.name,
                            "description": sub.description or "No Description.",
                            "type": model.SlashCommandOptionType.SUB_COMMAND,
                            "options": sub.options or []
                        }
                        output[guild][command_name]["options"].append(_dict)

                    else:
                        queue = {}
                        base_dict = {
                            "name": subcommand_name,
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
                            if guild not in queue:
                                queue[guild] = copy.deepcopy(base_dict)
                            queue[guild]["options"].append(_dict)
                        for i in queue:
                            output[i][command_name]["options"].append(queue[guild])
        for subcommand_name in output:
            if subcommand_name == "global":
                [cmds['global'].append(n) for n in output['global'].values()]
            else:
                [cmds['guild'][subcommand_name].append(n) for n in output[subcommand_name].values()]
        return cmds

    async def sync_all_commands(self, delete_from_unused_guilds=False):
        """
        Matches commands registered on Discord to commands registered here.
        Deletes any commands on Discord but not here, and registers any not on Discord.
        This is done with a `put` request.
        If ``sync_commands`` is ``True``, then this will be automatically called.

        :param delete_from_unused_guilds: If the bot should make a request to set no commands for guilds that haven't got any commands registered in :class:``SlashCommand``
        """
        cmds = await self.to_dict()
        self.logger.info("Syncing commands...")
        other_guilds = [x.id for x in self._discord.guilds if x.id not in cmds["guild"]]
        # This is an extremely bad way to do this, because slash cmds can be in guilds the bot isn't in
        # But it's the only way until discord makes an endpoint to request all the guild with cmds registered.

        self.logger.debug("Syncing global commands...")
        await self.req.put_slash_commands(slash_commands=cmds["global"], guild_id=None)

        for guild in cmds["guild"]:
            self.logger.debug(f"Syncing commands for {guild}")
            _cmds = cmds["guild"][guild]
            if _cmds:
                await self.req.put_slash_commands(slash_commands=_cmds, guild_id=guild)
        if delete_from_unused_guilds:
            for x in other_guilds:
                with suppress(discord.Forbidden):
                    await self.req.put_slash_commands(slash_commands=[], guild_id=x)

        self.logger.info("Completed syncing all commands!")

    def add_slash_command(self,
                          cmd,
                          name: str = None,
                          description: str = None,
                          guild_ids: typing.List[int] = None,
                          options: list = None,
                          connector: dict = None,
                          has_subcommands: bool = False):
        """
        Registers slash command to SlashCommand.

        ..warning::
            Just using this won't register slash command to Discord API.
            To register it, check :meth:`.utils.manage_commands.add_slash_command` or simply enable `sync_commands`.

        :param cmd: Command Coroutine.
        :type cmd: Coroutine
        :param name: Name of the slash command. Default name of the coroutine.
        :type name: str
        :param description: Description of the slash command. Defaults to command docstring or ``None``.
        :type description: str
        :param guild_ids: List of Guild ID of where the command will be used. Default ``None``, which will be global command.
        :type guild_ids: List[int]
        :param options: Options of the slash command. This will affect ``auto_convert`` and command data at Discord API. Default ``None``.
        :type options: list
        :param connector: Kwargs connector for the command. Default ``None``.
        :type connector: dict
        :param has_subcommands: Whether it has subcommand. Default ``False``.
        :type has_subcommands: bool
        """
        name = name or cmd.__name__
        name = name.lower()
        guild_ids = guild_ids if guild_ids else ["global"]
        cp_guild_ids = guild_ids.copy()

        for guild in cp_guild_ids:
            if guild is None:
                guild = "global"

            if guild not in self.commands:
                self.commands[guild] = {}
            if name in self.commands[guild]:
                # prevent duplicate commands in guild
                tgt = self.commands[guild][name]
                if not tgt.has_subcommands:
                    raise error.DuplicateCommand(name)
                has_subcommands = tgt.has_subcommands
                for x in tgt.allowed_guild_ids:
                    if x not in guild_ids:
                        guild_ids.append(x)

        description = description or getdoc(cmd)

        if options is None:
            options = manage_commands.generate_options(cmd, description, connector)

        _cmd = {
            "func": cmd,
            "description": description,
            "guild_ids": guild_ids,
            "api_options": options,
            "connector": connector or {},
            "has_subcommands": has_subcommands
        }
        obj = model.CommandObject(name, _cmd)

        for guild in guild_ids:
            self.commands[guild][name] = obj
            self.logger.debug(f"{str(guild).center(18)} :: Added command `{name}`")
        return obj

    def add_subcommand(self,
                       cmd,
                       base,
                       subcommand_group=None,
                       name=None,
                       description: str = None,
                       base_description: str = None,
                       subcommand_group_description: str = None,
                       guild_ids: typing.List[int] = None,
                       options: list = None,
                       connector: dict = None):
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
        :param guild_ids: List of guild ID of where the command will be used. Default ``None``, which will be global command.
        :type guild_ids: List[int]
        :param options: Options of the subcommand. This will affect ``auto_convert`` and command data at Discord API. Default ``None``.
        :type options: list
        :param connector: Kwargs connector for the command. Default ``None``.
        :type connector: dict
        """
        base = base.lower()
        subcommand_group = subcommand_group.lower() if subcommand_group else subcommand_group
        name = name or cmd.__name__
        name = name.lower()
        description = description or getdoc(cmd)
        guild_ids = guild_ids if guild_ids else ["global"]

        for i in range(len(guild_ids)):
            if guild_ids[i] is None:
                guild_ids[i] = "global"
            if guild_ids[i] not in self.commands:
                self.commands[guild_ids[i]] = {}
            if guild_ids[i] not in self.subcommands:
                self.subcommands[guild_ids[i]] = {}
            if base in self.commands[guild_ids[i]]:
                for x in guild_ids:
                    if x not in self.commands[guild_ids[i]][base].allowed_guild_ids:
                        self.commands[guild_ids[i]][base].allowed_guild_ids.append(x)

        if options is None:
            options = manage_commands.generate_options(cmd, description, connector)

        _cmd = {
            "func": None,
            "description": base_description,
            "guild_ids": guild_ids.copy(),
            "api_options": [],
            "connector": {},
            "has_subcommands": True
        }
        _sub = {
            "func": cmd,
            "name": name,
            "description": description,
            "base_desc": base_description,
            "sub_group_desc": subcommand_group_description,
            "guild_ids": guild_ids,
            "api_options": options,
            "connector": connector or {}
        }
        for guild in guild_ids:
            if base not in self.commands[guild]:
                self.commands[guild][base] = model.CommandObject(base, _cmd)
            else:
                self.commands[guild][base].has_subcommands = True
                if self.commands[guild][base].description:
                    _cmd["description"] = self.commands[guild][base].description
            if base not in self.subcommands[guild]:
                self.subcommands[guild][base] = {}
            if subcommand_group:
                if subcommand_group not in self.subcommands[guild][base]:
                    self.subcommands[guild][base][subcommand_group] = {}
                if name in self.subcommands[guild][base][subcommand_group]:
                    raise error.DuplicateCommand(f"{guild} {base} {subcommand_group} {name}")
                obj = model.SubcommandObject(_sub, base, name, subcommand_group)
                self.subcommands[guild][base][subcommand_group][name] = obj
            else:
                if name in self.subcommands[guild][base]:
                    raise error.DuplicateCommand(f"{base} {name}")
                obj = model.SubcommandObject(_sub, base, name)
                self.subcommands[guild][base][name] = obj
            self.logger.debug(f"Added subcommand `{base} {subcommand_group or ''} {name or cmd.__name__}`")
        return obj

    def slash(self,
              *,
              name: str = None,
              description: str = None,
              guild_ids: typing.List[int] = None,
              options: typing.List[dict] = None,
              connector: dict = None):
        """
        Decorator that registers coroutine as a slash command.\n
        All decorator args must be passed as keyword-only args.\n
        1 arg for command coroutine is required for ctx(:class:`.model.SlashContext`),
        and if your slash command has some args, then those args are also required.\n
        All args must be passed as keyword-args.

        .. note::
            If you don't pass `options` but has extra args, then it will automatically generate options.
            However, it is not recommended to use it since descriptions will be "No Description." or the command's description.

        .. warning::
            Unlike discord.py's command, ``*args``, keyword-only args, converters, etc. are not supported or behave differently.

        Example:

        .. code-block:: python

            @slash.slash(name="ping")
            async def _slash(ctx): # Normal usage.
                await ctx.send(content=f"Pong! (`{round(bot.latency*1000)}`ms)")


            @slash.slash(name="pick")
            async def _pick(ctx, choice1, choice2): # Command with 1 or more args.
                await ctx.send(content=str(random.choice([choice1, choice2])))

        To format the connector, follow this example.

        .. code-block:: python

            {
                "example-arg": "example_arg",
                "시간": "hour"
                # Formatting connector is required for
                # using other than english for option parameter name
                # for in case.
            }

        Set discord UI's parameter name as key, and set command coroutine's arg name as value.

        :param name: Name of the slash command. Default name of the coroutine.
        :type name: str
        :param description: Description of the slash command. Default ``None``.
        :type description: str
        :param guild_ids: List of Guild ID of where the command will be used. Default ``None``, which will be global command.
        :type guild_ids: List[int]
        :param options: Options of the slash command. This will affect ``auto_convert`` and command data at Discord API. Default ``None``.
        :type options: List[dict]
        :param connector: Kwargs connector for the command. Default ``None``.
        :type connector: dict
        """

        def wrapper(cmd):
            obj = self.add_slash_command(cmd, name, description, guild_ids, options, connector)
            return obj

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
                   guild_ids: typing.List[int] = None,
                   options: typing.List[dict] = None,
                   connector: dict = None):
        """
        Decorator that registers subcommand.\n
        Unlike discord.py, you don't need base command.\n
        All args must be passed as keyword-args.

        .. note::
            If you don't pass `options` but has extra args, then it will automatically generate options.
            However, it is not recommended to use it since descriptions will be "No Description." or the command's description.

        .. warning::
            Unlike discord.py's command, ``*args``, keyword-only args, converters, etc. are not supported or behave differently.

        Example:

        .. code-block:: python

            # /group say <str>
            @slash.subcommand(base="group", name="say")
            async def _group_say(ctx, _str):
                await ctx.send(content=_str)

            # /group kick user <user>
            @slash.subcommand(base="group",
                              subcommand_group="kick",
                              name="user")
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
        :param guild_ids: List of guild ID of where the command will be used. Default ``None``, which will be global command.
        :type guild_ids: List[int]
        :param options: Options of the subcommand. This will affect ``auto_convert`` and command data at Discord API. Default ``None``.
        :type options: List[dict]
        :param connector: Kwargs connector for the command. Default ``None``.
        :type connector: dict
        """
        base_description = base_description or base_desc
        subcommand_group_description = subcommand_group_description or sub_group_desc

        def wrapper(cmd):
            obj = self.add_subcommand(cmd, base, subcommand_group, name, description, base_description,
                                      subcommand_group_description, guild_ids, options, connector)
            return obj

        return wrapper

    async def process_options(self, guild: discord.Guild, options: list, connector: dict,
                              temporary_auto_convert: dict = None) -> dict:
        """
        Processes Role, User, and Channel option types to discord.py's models.

        :param guild: Guild of the command message.
        :type guild: discord.Guild
        :param options: Dict of options.
        :type options: list
        :param connector: Kwarg connector.
        :param temporary_auto_convert: Temporary parameter, use this if options doesn't have ``type`` keyword.
        :return: Union[list, dict]
        """

        if not guild or not isinstance(guild, discord.Guild):
            return {connector.get(x["name"]) or x["name"]: x["value"] for x in options}

        converters = [
            # If extra converters are added and some needs to fetch it,
            # you should pass as a list with 1st item as a cache get method
            # and 2nd as a actual fetching method.
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

        to_return = {}

        for x in options:
            processed = None  # This isn't the best way, but we should to reduce duplicate lines.

            # This is to temporarily fix Issue #97, that on Android device
            # does not give option type from API.
            if "type" not in x:
                x["type"] = temporary_auto_convert[x["name"]]

            if x["type"] not in types:
                processed = x["value"]
            else:
                loaded_converter = converters[types[x["type"]]]
                if isinstance(loaded_converter, list):  # For user type.
                    cache_first = loaded_converter[0](int(x["value"]))
                    if cache_first:
                        processed = cache_first
                    else:
                        loaded_converter = loaded_converter[1]
                if not processed:
                    try:
                        processed = await loaded_converter(int(x["value"])) \
                            if iscoroutinefunction(loaded_converter) else \
                            loaded_converter(int(x["value"]))
                    except (discord.Forbidden, discord.HTTPException, discord.NotFound):  # Just in case.
                        self.logger.warning("Failed fetching discord object! Passing ID instead.")
                        processed = int(x["value"])
            to_return[connector.get(x["name"]) or x["name"]] = processed
        return to_return

    async def invoke_command(self, func, ctx, args):
        """
        Invokes command.

        :param func: Command coroutine.
        :param ctx: Context.
        :param args: Args. Can be list or dict.
        """
        try:
            not_kwargs = False
            if isinstance(args, dict):
                ctx.kwargs = args
                ctx.args = list(args.values())
                try:
                    await func.invoke(ctx, **args)
                except TypeError:
                    args = list(args.values())
                    not_kwargs = True
            else:
                ctx.args = args
                not_kwargs = True
            if not_kwargs:
                await func.invoke(ctx, *args)
        except Exception as ex:
            await self.on_slash_command_error(ctx, ex)

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

        ctx = context.SlashContext(self.req, to_use, self._discord, self.logger)
        cmd_name = to_use["data"]["name"]

        selected_cmd = None

        # check Global for command
        if cmd_name in self.commands["global"]:
            selected_cmd = self.commands["global"][cmd_name]
        # check guildID for command
        if ctx.guild_id in self.commands and \
                cmd_name in self.commands[ctx.guild_id]:
            if selected_cmd:
                # flag warning if theres a duplicate command in guild commands
                # if discord adds data signifying if a cmd is global or not we can remove this
                if not selected_cmd.has_subcommands:
                    # silence warning if cmd has subcmd, as this will be handled by handle_subcommand
                    self.logger.warning(f"Command in {ctx.guild_id} and Global share the name "
                                        f"\"{cmd_name}\", Global command will be used")
            else:
                selected_cmd = self.commands[ctx.guild_id][cmd_name]

        # command not in self.commands, might be a subcommand
        if not selected_cmd:
            if (ctx.guild_id in self.subcommands and cmd_name in self.subcommands[ctx.guild_id]) or \
                    cmd_name in self.subcommands[ctx.guild_id]:
                return await self.handle_subcommand(ctx, to_use)
            else:
                # command not found
                return

        if selected_cmd.allowed_guild_ids and "global" not in selected_cmd.allowed_guild_ids:
            if selected_cmd.allowed_guild_ids and ctx.guild_id not in selected_cmd.allowed_guild_ids:
                return

        if selected_cmd.has_subcommands and not selected_cmd.func:
            return await self.handle_subcommand(ctx, to_use)

        if "options" in to_use["data"]:
            for x in to_use["data"]["options"]:
                if "value" not in x:
                    return await self.handle_subcommand(ctx, to_use)

        # This is to temporarily fix Issue #97, that on Android device
        # does not give option type from API.
        temporary_auto_convert = {}
        for x in selected_cmd.options:
            temporary_auto_convert[x["name"].lower()] = x["type"]

        args = await self.process_options(ctx.guild, to_use["data"]["options"], selected_cmd.connector,
                                          temporary_auto_convert) \
            if "options" in to_use["data"] else {}

        self._discord.dispatch("slash_command", ctx)

        await self.invoke_command(selected_cmd, ctx, args)

    async def handle_subcommand(self, ctx: context.SlashContext, data: dict):
        """
        Coroutine for handling subcommand.

        .. warning::
            Do not manually call this.

        :param ctx: :class:`.model.SlashContext` instance.
        :param data: Gateway message.
        """
        basecmd_name = data["data"]["name"]
        subcmd_name = data["data"]["options"][0]["name"]
        local = None

        # check Global for sub-cmd
        if basecmd_name in self.subcommands["global"]:
            if subcmd_name in self.subcommands["global"][basecmd_name]:
                local = "global"
        # check guildID for command
        if ctx.guild_id in self.subcommands and basecmd_name in self.subcommands[ctx.guild_id]:
            if subcmd_name in self.subcommands[ctx.guild_id][basecmd_name]:
                if local:
                    # flag warning if theres a duplicate command in guild commands
                    # if discord adds data signifying if a cmd is global or not we can remove this
                    self.logger.warning(f"Subcommand in {ctx.guild_id} and Global share the name "
                                        f"\"{basecmd_name}\", Global subcommand will be used")
                else:
                    local = ctx.guild_id

        base = self.subcommands[local][data["data"]["name"]]
        sub = data["data"]["options"][0]
        sub_name = sub["name"]
        if sub_name not in base:
            return
        ctx.subcommand_name = sub_name
        sub_opts = sub["options"] if "options" in sub else []
        for x in sub_opts:
            if "options" in x or "value" not in x:
                sub_group = x["name"]
                if sub_group not in base[sub_name]:
                    return
                ctx.subcommand_group = sub_group
                selected = base[sub_name][sub_group]

                # This is to temporarily fix Issue #97, that on Android device
                # does not give option type from API.
                temporary_auto_convert = {}
                for n in selected.options:
                    temporary_auto_convert[n["name"].lower()] = n["type"]

                args = await self.process_options(ctx.guild, x["options"], selected.connector, temporary_auto_convert) \
                    if "options" in x else {}
                self._discord.dispatch("slash_command", ctx)
                await self.invoke_command(selected, ctx, args)
                return
        selected = base[sub_name]

        # This is to temporarily fix Issue #97, that on Android device
        # does not give option type from API.
        temporary_auto_convert = {}
        for n in selected.options:
            temporary_auto_convert[n["name"].lower()] = n["type"]

        args = await self.process_options(ctx.guild, sub_opts, selected.connector, temporary_auto_convert) \
            if "options" in sub else {}
        self._discord.dispatch("slash_command", ctx)
        await self.invoke_command(selected, ctx, args)

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
        # Prints exception if not overridden or has no listener for error.
        self.logger.exception(f"An exception has occurred while executing command `{ctx.name}`:")
