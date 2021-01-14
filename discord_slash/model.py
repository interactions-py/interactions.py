import typing
import asyncio
import discord
from enum import IntEnum
from contextlib import suppress
from discord.ext import commands
from . import http
from . import error


class SlashContext:
    """
    Context of the slash command.\n
    Kinda similar with discord.ext.commands.Context.

    .. warning::
        Do not manually init this model.

    :ivar name: Name of the command.
    :ivar subcommand_name: Subcommand of the command.
    :ivar subcommand_group: Subcommand group of the command.
    :ivar interaction_id: Interaction ID of the command message.
    :ivar command_id: ID of the command.
    :ivar _http: :class:`.http.SlashCommandRequest` of the client.
    :ivar bot: discord.py client.
    :ivar logger: Logger instance.
    :ivar sent: Whether you sent the initial response.
    :ivar guild: :class:`discord.Guild` instance or guild ID of the command message.
    :ivar author: :class:`discord.Member` instance or user ID representing author of the command message.
    :ivar channel: :class:`discord.TextChannel` instance or channel ID representing channel of the command message.
    """

    def __init__(self,
                 _http: http.SlashCommandRequest,
                 _json: dict,
                 _discord: typing.Union[discord.Client, commands.Bot],
                 logger):
        self.__token = _json["token"]
        self.message = None # Should be set later.
        self.name = self.command = self.invoked_with = _json["data"]["name"]
        self.subcommand_name = self.invoked_subcommand = self.subcommand_passed = None
        self.subcommand_group = self.invoked_subcommand_group = self.subcommand_group_passed = None
        self.interaction_id = _json["id"]
        self.command_id = _json["data"]["id"]
        self._http = _http
        self.bot = _discord
        self.logger = logger
        self.sent = False
        self.guild: typing.Union[discord.Guild, int] = _discord.get_guild(int(_json["guild_id"]))
        self.author: typing.Union[discord.Member, int] = self.guild.get_member(int(_json["member"]["user"]["id"])) \
            if self.guild else None
        self.channel: typing.Union[discord.TextChannel, int] = self.guild.get_channel(int(_json["channel_id"])) \
            if self.guild else None
        if not self.author:
            self.author = int(_json["member"]["user"]["id"])
        if not self.channel:
            self.channel = int(_json["channel_id"])
        if not self.guild:
            # Should be set after every others are set.
            self.guild = int(_json["guild_id"])

    async def respond(self, eat: bool = False):
        """
        Sends command invoke response.\n
        You should call this first.

        .. note::
            If `eat` is ``False``, there is a chance that ``message`` variable is present.

        :param eat: Whether to eat user's input. Default ``False``.
        """
        base = {"type": 2 if eat else 5}
        self.bot.loop.create_task(self._http.post(base, self.bot.user.id, self.interaction_id, self.__token, True))
        self.sent = True
        if not eat:
            with suppress(asyncio.TimeoutError):
                def check(message: discord.Message):
                    user_id = self.author if isinstance(self.author, int) else self.author.id
                    is_author = message.author.id == user_id
                    channel_id = self.channel if isinstance(self.channel, int) else self.channel.id
                    is_channel = channel_id == message.channel.id
                    is_user_input = message.type == 20
                    is_correct_command = message.content.startswith(f"</{self.name}:{self.command_id}>")
                    return is_author and is_channel and is_user_input and is_correct_command

                self.message = await self.bot.wait_for("message", timeout=3, check=check)

    @property
    def ack(self):
        """Alias of :meth:`.respond`."""
        return self.respond

    async def send(self):
        raise NotImplementedError

    async def edit_original(self,
                            *,
                            content: str = "",
                            embeds: typing.List[discord.Embed] = None,
                            tts: bool = False,
                            allowed_mentions: discord.AllowedMentions = None):
        """
        Edits response of the slash command.

        .. note::
            All args must be passed as keyword args.

        :param content: Text of the response. Can be ``None``.
        :type content: str
        :param embeds: Embeds of the response. Maximum 10, can be empty.
        :type embeds: List[discord.Embed]
        :param tts: Whether to speak message using tts. Default ``False``.
        :type tts: bool
        :param allowed_mentions: AllowedMentions of the message.
        :type allowed_mentions: discord.AllowedMentions
        :return: ``None``
        """
        if embeds and len(embeds) > 10:
            raise error.IncorrectFormat("Embed must be 10 or fewer.")
        base = {
            "content": content,
            "tts": tts,
            "embeds": [x.to_dict() for x in embeds] if embeds else [],
            "allowed_mentions": allowed_mentions.to_dict() if allowed_mentions
            else self.bot.allowed_mentions.to_dict() if self.bot.allowed_mentions else {}
        }
        await self._http.edit(base, self.bot.user.id, self.__token, "@original")

    async def delete_original(self):
        """
        Deletes response of the slash command.

        :param message_id: Response message ID. Default initial message.
        :return: ``None``
        """
        await self._http.delete(self.bot.user.id, self.__token, "@original")


class CommandObject:
    """
    Slash command object of this extension.

    .. warning::
        Do not manually init this model.

    :ivar name: Name of the command.
    :ivar func: The coroutine of the command.
    :ivar description: Description of the command.
    :ivar auto_convert: Dictionary of the `auto_convert` of the command.
    :ivar allowed_guild_ids: List of the allowed guild id.
    :ivar options: List of the option of the command. Used for `auto_register`.
    """
    def __init__(self, name, cmd):  # Let's reuse old command formatting.
        self.name = name.lower()
        self.func = cmd["func"]
        self.description = cmd["description"]
        self.auto_convert = cmd["auto_convert"] or {}
        self.allowed_guild_ids = cmd["guild_ids"] or []
        self.options = cmd["api_options"] or []
        self.has_subcommands = cmd["has_subcommands"]

    def invoke(self, *args):
        """
        Invokes the command.

        :param args: Args for the command.
        :return: Coroutine
        """
        return self.func(*args)


class SubcommandObject:
    """
    Subcommand object of this extension.

    .. warning::
        Do not manually init this model.

    :ivar base: Name of the base slash command.
    :ivar subcommand_group: Name of the subcommand group. ``None`` if not exist.
    :ivar name: Name of the subcommand.
    :ivar func: The coroutine of the command.
    :ivar description: Description of the command.
    :ivar base_description: Description of the base command.
    :ivar subcommand_group_description: Description of the subcommand_group.
    :ivar auto_convert: Dictionary of the `auto_convert` of the command.
    :ivar allowed_guild_ids: List of the allowed guild id.
    """
    def __init__(self, sub, base, name, sub_group=None):
        self.base = base.lower()
        self.subcommand_group = sub_group.lower() if sub_group else sub_group
        self.name = name.lower()
        self.func = sub["func"]
        self.description = sub["description"]
        self.base_description = sub["base_desc"]
        self.subcommand_group_description = sub["sub_group_desc"]
        self.auto_convert = sub["auto_convert"] or {}
        self.allowed_guild_ids = sub["guild_ids"] or []
        self.options = sub["api_options"] or []

    def invoke(self, *args):
        """
        Invokes the command.

        :param args: Args for the command.
        :return: Coroutine
        """
        return self.func(*args)


class CogCommandObject(CommandObject):
    """
    Slash command object but for Cog.

    .. warning::
        Do not manually init this model.
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.cog = None  # Manually set this later.

    def invoke(self, *args):
        """
        Invokes the command.

        :param args: Args for the command.
        :return: Coroutine
        """
        return self.func(self.cog, *args)


class CogSubcommandObject(SubcommandObject):
    """
    Subcommand object but for Cog.

    .. warning::
        Do not manually init this model.
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.cog = None  # Manually set this later.

    def invoke(self, *args):
        """
        Invokes the command.

        :param args: Args for the command.
        :return: Coroutine
        """
        return self.func(self.cog, *args)


class SlashCommandOptionType(IntEnum):
    """
    Equivalent of `ApplicationCommandOptionType <https://discord.com/developers/docs/interactions/slash-commands#applicationcommandoptiontype>`_  in the Discord API.
    """
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8

    @classmethod
    def from_type(cls, t: type):
        """
        Get a specific SlashCommandOptionType from a type (or object).

        :param t: The type or object to get a SlashCommandOptionType for.
        :return: :class:`.model.SlashCommandOptionType` or ``None``
        """
        if issubclass(t, str): return cls.STRING
        if issubclass(t, int): return cls.INTEGER
        if issubclass(t, bool): return cls.BOOLEAN
        if issubclass(t, discord.abc.User): return cls.USER
        if issubclass(t, discord.abc.GuildChannel): return cls.CHANNEL
        if issubclass(t, discord.abc.Role): return cls.ROLE
