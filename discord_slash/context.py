import typing
import asyncio
import aiohttp
import discord
from contextlib import suppress
from discord import Webhook, AsyncWebhookAdapter, WebhookMessage
from discord.ext import commands
from . import http
from . import error


class SlashContext:
    """
    Context of the slash command.\n
    Kinda similar with discord.ext.commands.Context.

    .. warning::
        Do not manually init this model.

    :ivar message: Message that invoked the slash command.
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
        _task = self.bot.loop.create_task(self._http.post(base, False, self.bot.user.id, self.interaction_id, self.__token, True))
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
        await _task

    @property
    def ack(self):
        """Alias of :meth:`.respond`."""
        return self.respond

    async def send(self,
                   content: str = "", *,
                   wait: bool = False,
                   embed: discord.Embed = None,
                   embeds: typing.List[discord.Embed] = None,
                   tts: bool = False,
                   file: discord.File = None,
                   files: typing.List[discord.File] = None,
                   allowed_mentions: discord.AllowedMentions = None,
                   hidden: bool = False) -> typing.Union[discord.Message, dict]:
        """
        Sends response of the slash command.

        .. note::
            - Param ``hidden`` doesn't support embed.

        .. warning::
            - Since Release 1.0.9, this is completely changed. If you are migrating from older that that, please make sure to fix the usage.
            - You can't use both ``embed`` and ``embeds`` at the same time, also applies to ``file`` and ``files``.

        :param content:  Content of the response.
        :type content: str
        :param wait: Whether the server should wait before sending a response.
        :param embed: Embed of the response.
        :type embed: discord.Embed
        :param embeds: Embeds of the response. Maximum 10.
        :type embeds: List[discord.Embed]
        :param tts: Whether to speak message using tts. Default ``False``.
        :type tts: bool
        :param file: File to send.
        :type file: discord.File
        :param files: Files to send.
        :type files: List[discord.File]
        :param allowed_mentions: AllowedMentions of the message.
        :type allowed_mentions: discord.AllowedMentions
        :param hidden: Whether the message is hidden, which means message content will only be seen to the author.
        :type hidden: bool
        :return: Union[discord.Message, dict]
        """
        if not self.sent:
            self.logger.warning(f"At command `{self.name}`: It is highly recommended to call `.respond()` first!")
            await self.respond()
        if hidden:
            if embeds or embed:
                self.logger.warning("Embed is not supported for `hidden`!")
            return await self.send_hidden(content)
        if embed and embeds:
            raise error.IncorrectFormat("You can't use both `embed` and `embeds`!")
        if embed:
            embeds = [embed]
        if embeds:
            if not isinstance(embeds, list):
                raise error.IncorrectFormat("Provide a list of embeds.")
            elif len(embeds) > 10:
                raise error.IncorrectFormat("Do not provide more than 10 embeds.")
        if file and files:
            raise error.IncorrectFormat("You can't use both `file` and `files`!")
        if file:
            files = [file]

        base = {
            "content": content,
            "tts": tts,
            "embeds": [x.to_dict() for x in embeds] if embeds else [],
            "allowed_mentions": allowed_mentions.to_dict() if allowed_mentions
            else self.bot.allowed_mentions.to_dict() if self.bot.allowed_mentions else {}
        }

        resp = await self._http.post(base, wait, self.bot.user.id, self.interaction_id, self.__token, files=files)
        print(resp)
        try:
            if isinstance(self.channel, discord.TextChannel) and isinstance(resp, dict):
                return await self.channel.fetch_message(resp["id"])
            return resp
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            return resp

    def _legacy_send(self, content, tts, embeds, allowed_mentions):
        base = {
            "content": content,
            "tts": tts,
            "embeds": [x.to_dict() for x in embeds] if embeds else [],
            "allowed_mentions": allowed_mentions.to_dict() if allowed_mentions
            else self.bot.allowed_mentions.to_dict() if self.bot.allowed_mentions else {}
        }
        return self._http.post(base, True, self.bot.user.id, self.interaction_id, self.__token)

    def send_hidden(self, content: str = ""):
        base = {
            "content": content,
            "flags": 64
        }
        return self._http.post(base, False, self.bot.user.id, self.interaction_id, self.__token)
