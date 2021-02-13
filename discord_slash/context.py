import typing
import asyncio
import discord
from contextlib import suppress
from discord.ext import commands
from . import http
from . import error
from . import model


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
    :ivar guild_id: Guild ID of the command message. If the command was invoked in DM, then it is ``None``
    :ivar author_id: User ID representing author of the command message.
    :ivar channel_id: Channel ID representing channel of the command message.
    :ivar author: User or Member instance of the command invoke.
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
        self.guild_id = int(_json["guild_id"]) if "guild_id" in _json.keys() else None
        self.author_id = int(_json["member"]["user"]["id"] if "member" in _json.keys() else _json["user"]["id"])
        self.channel_id = int(_json["channel_id"])
        if self.guild:
            self.author = discord.Member(data=_json["member"], state=self.bot._connection, guild=self.guild)
        else:
            self.author = discord.User(data=_json["user"], state=self.bot._connection)

    @property
    def guild(self) -> typing.Optional[discord.Guild]:
        """
        Guild instance of the command invoke. If the command was invoked in DM, then it is ``None``

        :return: Optional[discord.Guild]
        """
        return self.bot.get_guild(self.guild_id) if self.guild_id else None

    @property
    def channel(self) -> typing.Optional[typing.Union[discord.abc.GuildChannel, discord.abc.PrivateChannel]]:
        """
        Channel instance of the command invoke.

        :return: Optional[Union[discord.abc.GuildChannel, discord.abc.PrivateChannel]]
        """
        return self.bot.get_channel(self.channel_id)

    async def respond(self, eat: bool = False):
        """
        Sends command invoke response.\n
        You should call this first.

        .. note::
            - If `eat` is ``False``, there is a chance that ``message`` variable is present.
            - While it is recommended to be manually called, this will still be automatically called
              if this isn't called but :meth:`.send()` is called.

        :param eat: Whether to eat user's input. Default ``False``.
        """
        base = {"type": 2 if eat else 5}
        _task = self.bot.loop.create_task(self._http.post(base, self.interaction_id, self.__token, True))
        self.sent = True
        if not eat:
            with suppress(asyncio.TimeoutError):
                def check(message: discord.Message):
                    user_id = self.author_id
                    is_author = message.author.id == user_id
                    channel_id = self.channel_id
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
                   embed: discord.Embed = None,
                   embeds: typing.List[discord.Embed] = None,
                   tts: bool = False,
                   file: discord.File = None,
                   files: typing.List[discord.File] = None,
                   allowed_mentions: discord.AllowedMentions = None,
                   hidden: bool = False,
                   delete_after: float = None) -> model.SlashMessage:
        """
        Sends response of the slash command.

        .. note::
            - Param ``hidden`` doesn't support embed and file.

        .. warning::
            - Since Release 1.0.9, this is completely changed. If you are migrating from older version, please make sure to fix the usage.
            - You can't use both ``embed`` and ``embeds`` at the same time, also applies to ``file`` and ``files``.

        :param content:  Content of the response.
        :type content: str
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
        :param delete_after: If provided, the number of seconds to wait in the background before deleting the message we just sent. If the deletion fails, then it is silently ignored.
        :type delete_after: float
        :return: Union[discord.Message, dict]
        """
        if isinstance(content, int) and 2 <= content <= 5:
            raise error.IncorrectFormat("`.send` Method is rewritten at Release 1.0.9. Please read the docs and fix all the usages.")
        if not self.sent:
            self.logger.info(f"At command `{self.name}`: It is recommended to call `.respond()` first!")
            await self.respond(eat=hidden)
        if hidden:
            if embeds or embed or files or file:
                self.logger.warning("Embed/File is not supported for `hidden`!")
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

        resp = await self._http.post(base, self.interaction_id, self.__token, files=files)
        smsg = model.SlashMessage(state=self.bot._connection,
                                  data=resp,
                                  channel=self.channel or discord.Object(id=self.channel),
                                  _http=self._http,
                                  interaction_token=self.__token)
        if delete_after:
            self.bot.loop.create_task(smsg.delete(delay=delete_after))
        return smsg

    def send_hidden(self, content: str = ""):
        """
        Sends hidden response.\n
        This is automatically used if you pass ``hidden=True`` at :meth:`.send`.

        :param content: Message content.
        :return: Coroutine
        """
        base = {
            "content": content,
            "flags": 64
        }
        return self._http.post(base, self.interaction_id, self.__token)
