import typing
import asyncio
import discord
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

    async def send(self,
                   content: str = "", *,
                   wait: bool = True,
                   embed: discord.Embed = None,
                   embeds: typing.List[discord.Embed] = None,
                   tts: bool = False,
                   allowed_mentions: discord.AllowedMentions = None,
                   hidden: bool = False):
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
        """
        await self._http.delete(self.bot.user.id, self.__token, "@original")
