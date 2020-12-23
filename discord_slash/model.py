import typing
import discord
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
    :ivar _discord: :class:`discord.ext.commands.Bot`
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
        self.name = _json["data"]["name"]
        self.subcommand_name = None
        self.subcommand_group = None
        self.interaction_id = _json["id"]
        self.command_id = _json["data"]["id"]
        self._http = _http
        self._discord = _discord
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

    async def send(self,
                   send_type: int = 4,
                   content: str = "",
                   *,
                   embeds: typing.List[discord.Embed] = None,
                   tts: bool = False,
                   allowed_mentions: discord.AllowedMentions = None,
                   hidden: bool = False,
                   complete_hidden: bool = False):
        """
        Sends response of the slash command.

        .. note::
            Every args except `send_type` and `content` must be passed as keyword args.

        .. warning::
            Param ``hidden`` only works without embeds.

        :param send_type: Type of the response. Refer Discord API DOCS for more info about types. Default ``4``.
        :type send_type: int
        :param content: Content of the response. Can be ``None``.
        :type content: str
        :param embeds: Embeds of the response. Maximum 10, can be empty.
        :type embeds: List[discord.Embed]
        :param tts: Whether to speak message using tts. Default ``False``.
        :type tts: bool
        :param allowed_mentions: AllowedMentions of the message.
        :type allowed_mentions: discord.AllowedMentions
        :param hidden: Whether the message is hidden, which means message content will only be seen to the author.
        :type hidden: bool
        :param complete_hidden: If this is ``True``, it will be both hidden and `send_type` will be 3. Default ``False``.
        :type complete_hidden: bool
        :return: ``None``
        """
        if embeds and len(embeds) > 10:
            raise error.IncorrectFormat("Embed must be 10 or fewer.")
        if complete_hidden:
            # Overrides both `hidden` and `send_type`.
            hidden = True
            send_type = 3
        base = {
            "type": send_type,
            "data": {
                "tts": tts,
                "content": content,
                "embeds": [x.to_dict() for x in embeds] if embeds else [],
                "allowed_mentions": allowed_mentions.to_dict() if allowed_mentions
                else self._discord.allowed_mentions.to_dict() if self._discord.allowed_mentions else {}
            }
        } if not self.sent else {
            "content": content,
            "tts": tts,
            "embeds": [x.to_dict() for x in embeds] if embeds else [],
            "allowed_mentions": allowed_mentions.to_dict() if allowed_mentions
            else self._discord.allowed_mentions.to_dict() if self._discord.allowed_mentions else {}
        }
        if hidden:
            if self.sent:
                base["flags"] = 64
            else:
                base["data"]["flags"] = 64
        if hidden and embeds:
            self.logger.warning("You cannot use both `hidden` and `embeds` at the same time!")
        if (send_type == 2 or send_type == 5) and not self.sent:
            base = {"type": send_type}
        initial = True if not self.sent else False
        resp = await self._http.post(base, self._discord.user.id, self.interaction_id, self.__token, initial)
        self.sent = True
        return resp

    async def edit(self,
                   *,
                   message_id: typing.Union[int, str] = "@original",
                   content: str = "",
                   embeds: typing.List[discord.Embed] = None,
                   tts: bool = False,
                   allowed_mentions: discord.AllowedMentions = None):
        """
        Edits response of the slash command.

        .. note::
            All args must be passed as keyword args.

        :param message_id: Response message ID. Default initial message.
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
            else self._discord.allowed_mentions.to_dict() if self._discord.allowed_mentions else {}
        }
        await self._http.edit(base, self._discord.user.id, self.__token, message_id)

    async def delete(self, message_id: typing.Union[int, str] = "@original"):
        """
        Deletes response of the slash command.

        :param message_id: Response message ID. Default initial message.
        :return: ``None``
        """
        await self._http.delete(self._discord.user.id, self.__token, message_id)


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
    def __init__(self, name, cmd): # Let's reuse old command formatting.
        self.name = name
        self.func = cmd["func"]
        self.description = cmd["description"]
        self.auto_convert = cmd["auto_convert"]
        self.allowed_guild_ids = cmd["guild_ids"]
        self.options = cmd["api_options"]
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
    :ivar auto_convert: Dictionary of the `auto_convert` of the command.
    :ivar allowed_guild_ids: List of the allowed guild id.
    """
    def __init__(self, sub, base, name, sub_group=None):
        self.base = base
        self.subcommand_group = sub_group
        self.name = name
        self.func = sub["func"]
        self.description = sub["description"]
        self.auto_convert = sub["auto_convert"]
        self.allowed_guild_ids = sub["guild_ids"]

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
        self.cog = None # Manually set this later.

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
        self.cog = None # Manually set this later.

    def invoke(self, *args):
        """
        Invokes the command.

        :param args: Args for the command.
        :return: Coroutine
        """
        return self.func(self.cog, *args)
