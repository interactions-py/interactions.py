import typing
import inspect
from .model import CogBaseCommandObject, CogSubcommandObject
from .utils import manage_commands


def cog_slash(*,
              name: str = None,
              description: str = None,
              guild_ids: typing.List[int] = None,
              options: typing.List[dict] = None,
              default_permission: bool = True,
              permissions: typing.Dict[int, list] = None,
              connector: dict = None):
    """
    Decorator for Cog to add slash command.\n
    Almost same as :func:`.client.SlashCommand.slash`.

    Example:

    .. code-block:: python

        class ExampleCog(commands.Cog):
            def __init__(self, bot):
                self.bot = bot

            @cog_ext.cog_slash(name="ping")
            async def ping(self, ctx: SlashContext):
                await ctx.send(content="Pong!")

    :param name: Name of the slash command. Default name of the coroutine.
    :type name: str
    :param description: Description of the slash command. Default ``None``.
    :type description: str
    :param guild_ids: List of Guild ID of where the command will be used. Default ``None``, which will be global command.
    :type guild_ids: List[int]
    :param options: Options of the slash command. This will affect ``auto_convert`` and command data at Discord API. Default ``None``.
    :type options: List[dict]
    :param default_permission: Sets if users have permission to run slash command by default, when no permissions are set. Default ``True``.
    :type default_permission: bool
    :param permissions: Dictionary of permissions of the slash command. Key being target guild_id and value being a list of permissions to apply. Default ``None``.
    :type permissions: dict
    :param connector: Kwargs connector for the command. Default ``None``.
    :type connector: dict
    """
    def wrapper(cmd):
        desc = description or inspect.getdoc(cmd)
        if options is None:
            opts = manage_commands.generate_options(cmd, desc, connector)
        else:
            opts = options

        if guild_ids is not None:
            if not all(isinstance(item, int) for item in guild_ids):
                raise Exception(f"The snowflake IDs {guild_ids} given are not a list of integers. Because of discord.py convention, please use integer IDs instead. Furthermore, the command '{name or cmd.__name__}' will be deactivated and broken until fixed.")

        _cmd = {
            "func": cmd,
            "description": desc,
            "guild_ids": guild_ids,
            "api_options": opts,
            "default_permission": default_permission,
            "api_permissions": permissions,
            "connector": connector,
            "has_subcommands": False
        }
        return CogBaseCommandObject(name or cmd.__name__, _cmd)
    return wrapper


def cog_subcommand(*,
                   base,
                   subcommand_group=None,
                   name=None,
                   description: str = None,
                   base_description: str = None,
                   base_desc: str = None,
                   base_default_permission: bool = True,
                   base_permissions: typing.Dict[int, list] = None,
                   subcommand_group_description: str = None,
                   sub_group_desc: str = None,
                   guild_ids: typing.List[int] = None,
                   options: typing.List[dict] = None,
                   connector: dict = None):
    """
    Decorator for Cog to add subcommand.\n
    Almost same as :func:`.client.SlashCommand.subcommand`.

    Example:

    .. code-block:: python

        class ExampleCog(commands.Cog):
            def __init__(self, bot):
                self.bot = bot

            @cog_ext.cog_subcommand(base="group", name="say")
            async def group_say(self, ctx: SlashContext, text: str):
                await ctx.send(content=text)

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
    :param base_default_permission: Sets if users have permission to run slash command by default, when no permissions are set. Default ``True``.
    :type base_default_permission: bool
    :param base_permissions: Dictionary of permissions of the slash command. Key being target guild_id and value being a list of permissions to apply. Default ``None``.
    :type base_permissions: dict
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
    guild_ids = guild_ids if guild_ids else []

    def wrapper(cmd):
        desc = description or inspect.getdoc(cmd)
        if options is None:
            opts = manage_commands.generate_options(cmd, desc, connector)
        else:
            opts = options

        if guild_ids is not None:
            if not all(isinstance(item, int) for item in guild_ids):
                raise Exception(f"The snowflake IDs {guild_ids} given are not a list of integers. Because of discord.py convention, please use integer IDs instead. Furthermore, the command '{name or cmd.__name__}' will be deactivated and broken until fixed.")

        _cmd = {
            "func": None,
            "description": base_description,
            "guild_ids": guild_ids.copy(),
            "api_options": [],
            "default_permission": base_default_permission,
            "api_permissions": base_permissions,
            "connector": {},
            "has_subcommands": True
        }

        _sub = {
            "func": cmd,
            "name": name or cmd.__name__,
            "description": desc,
            "base_desc": base_description,
            "sub_group_desc": subcommand_group_description,
            "guild_ids": guild_ids,
            "api_options": opts,
            "connector": connector
        }
        return CogSubcommandObject(base, _cmd, subcommand_group, name or cmd.__name__, _sub)
    return wrapper
