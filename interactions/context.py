# Normal libraries
from datetime import datetime
from logging import Logger
from typing import Any, List, Optional, Union
from warnings import warn

# 3rd-party libraries
from discord import (
    AllowedMentions,
    Client,
    ClientUser,
    Embed,
    File,
    AutoShardedClient,
    Guild,
    Member,
    Object,
    User
)
from discord.abc import GuildChannel, PrivateChannel
from discord.utils import snowflake_time
from discord.voice_client import VoiceProtocol
from .http import Command
from .error import InteractionException
from .model import Message
from .types.enums import DefaultErrorEnum as errorcode

class Interaction:
    """
    Object representing base context for interactions.

    .. warning::

        Do not manually initialize this class.

    :ivar token:
    :ivar message:
    :ivar interaction_id:
    :ivar bot:
    :ivar http:
    :ivar logger:
    :ivar data:
    :ivar values:
    :ivar deferred:
    :ivar deferred_hidden:
    :ivar responded:
    :ivar guild_id:
    :ivar author_id:
    :ivar channel_id:
    :ivar author:
    """
    __slots__ = (
        "token",
        "message",
        "interaction_id",
        "bot",
        "http",
        "logger",
        "data",
        "values",
        "deferred",
        "deferred_hidden",
        "responded",
        "guild_id",
        "author_id",
        "channel_id",
        "author"
    )
    token: str
    message: Optional[Any]
    interaction_id: int
    bot: Union[Client, AutoShardedClient]
    http: Command
    logger: Logger
    data: List[dict]
    values: Optional[List[dict]]
    deferred: bool
    deferred_hidden: bool
    responded: bool
    guild_id: int
    author_id: int
    channel_id: int
    author: Union[Member, User]
    created_at: datetime

    def __init__(
        self,
        _http: Command,
        _json: dict,
        _discord: Union[Client, AutoShardedClient],
        _logger: Logger
    ) -> None:
        """
        Instantiates the Interaction class.

        :param _http: The HTTP request parser for commands.
        :type _http: .http.Command
        :param _json: A dictionary set of keys and values.
        :type _json: dict
        :param _discord: The discord client to access.
        :type _discord: typing.Union[discord.Client, discord.AutoShardedClient]
        :param logger: Logger object for logging events.
        :type logger: logging.Logger
        :return: None
        """
        self.token = _json["token"]
        self.message = None
        self.data = _json["data"]
        self.interaction_id = _json["interaction_id"]
        self.http = _http
        self.bot = _discord
        self.logger = _logger
        self.deferred, self.deferred_hidden = False
        self.values = self.data["values"] if "values" in self.data else None
        self.guild_id = int(_json["guild_id"]) if "guild_id" in _json.keys() else None
        self.author_id = (
            _json["member"]["user"]["id"] if "member" in _json.keys() else _json["user"]["id"]
        )
        self.channel_id = int(_json["channel_id"])
        
        if self.guild:
            self.author = Member(
                data=_json["member"],
                state=self.bot._connection
            )
        elif self.guild_id:
            self.author = Member(
                data=_json["member"]["user"],
                state=self.bot._connection
            )
        else:
            self.author = User(
                data=_json["user"],
                state=self.bot._connection
            )
        self.created_at = snowflake_time(int(self.interaction_id))

    @property
    def _deffered_hidden(self):
        warn(
            "`_deffered_hidden` as been renamed to `_deferred_hidden`.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.deferred_hidden

    @_deffered_hidden.setter
    def _deffered_hidden(self, value):
        warn(
            "`_deffered_hidden` as been renamed to `_deferred_hidden`.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.deferred_hidden = value

    @property
    def deffered(self):
        warn("`deffered` as been renamed to `deferred`.", DeprecationWarning, stacklevel=2)
        return self.deferred

    @deffered.setter
    def deffered(self, value):
        warn("`deffered` as been renamed to `deferred`.", DeprecationWarning, stacklevel=2)
        self.deferred = value

    @property
    def deffered(self):
        warn("`deffered` as been renamed to `deferred`.", DeprecationWarning, stacklevel=2)
        return self.deferred

    @deffered.setter
    def deffered(self, value):
        warn("`deffered` as been renamed to `deferred`.", DeprecationWarning, stacklevel=2)
        self.deferred = value

    @property
    def guild(self) -> Optional[Guild]:
        """
        Guild instance of the command invoke. If the command was invoked in DM, then it is ``None``

        :return: typing.Optional[discord.Guild]
        """
        return self.bot.get_guild(self.guild_id) if self.guild_id else None

    @property
    def channel(self) -> Optional[Union[GuildChannel, PrivateChannel]]:
        """
        Channel instance of the command invoke.

        :return: typing.Optional[typing.Union[discord.abc.GuildChannel, discord.abc.PrivateChannel]]
        """
        return self.bot.get_channel(self.channel_id)

    @property
    def voice_client(self) -> Optional[VoiceProtocol]:
        """
        VoiceClient instance of the command invoke. If the command was invoked in DM, then it is ``None``.
        If the bot is not connected to any Voice/Stage channels, then it is ``None``.

        :return: typing.Optional[discord.VoiceProtocol]
        """
        return self.guild.voice_client if self.guild else None

    @property
    def me(self) -> Union[Member, ClientUser]:
        """
        Bot member instance of the command invoke. If the command was invoked in DM, then it is ``discord.ClientUser``.

        :return: typing.Union[discord.Member, discord.ClientUser]
        """
        return self.guild.me if self.guild is not None else self.bot.user

    async def defer(
        self,
        hidden: bool=False
    ) -> None:
        """
        "Defers" the interaction response, appearing as a loading state for the person who invoked the command.

        :param hidden: Whether the deferred response should be ephemeral. Defaults to ``False``.
        :type hidden: bool
        :return: None
        """
        if self.deferred or self.responded:
            raise InteractionException(errorcode.ALREADY_RESPONDED, message="You have already responded to this command!")

        base = {"type": 5}

        if hidden:
            base["data"] = {"flags": 64}
            self.deferred_hidden = True

        await self.http.add_initial_response(
            response=base, 
            interaction_id=self.interaction_id, 
            token=self.token
        )

        self.deferred = True

    """
    async def send(
        self,
        content: str = "",
        *,
        embed: Optional[Embed]=None,
        embeds: Optional[List[Embed]]=None,
        tts: bool = False,
        file: Optional[File]=None,
        files: Optional[List[File]]=None,
        allowed_mentions: Optional[AllowedMentions]=None,
        hidden: Optional[bool]=False,
        delete_after: Optional[float]=None,
        components: Optional[List[dict]]=None,
    ) -> Message:
    """
        
    """
        Sends response of the interaction.

        .. warning::
            - Since Release 1.0.9, this is completely changed. If you are migrating from older version, please make sure to fix the usage.
            - You can't use both ``embed`` and ``embeds`` at the same time, also applies to ``file`` and ``files``.
            - If you send files in the initial response, this will defer if it's not been deferred, and then PATCH with the message

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
        :param components: Message components in the response. The top level must be made of ActionRows.
        :type components: List[dict]
        :return: Union[discord.Message, dict]
    """

    """
        if embed and embeds:
            raise IncorrectFormat("You can't use both `embed` and `embeds`!")
        if embed:
            embeds = [embed]
        if embeds:
            if not isinstance(embeds, list):
                raise IncorrectFormat("Provide a list of embeds.")
            elif len(embeds) > 10:
                raise IncorrectFormat("Do not provide more than 10 embeds.")
        if file and files:
            raise IncorrectFormat("You can't use both `file` and `files`!")
        if file:
            files = [file]
        if delete_after and hidden:
            raise IncorrectFormat("You can't delete a hidden message!")
        if components and not all(comp.get("type") == 1 for comp in components):
            raise IncorrectFormat(
                "The top level of the components list must be made of ActionRows!"
            )

        if allowed_mentions is not None:
            if self.bot.allowed_mentions is not None:
                allowed_mentions = self.bot.allowed_mentions.merge(allowed_mentions).to_dict()
            else:
                allowed_mentions = allowed_mentions.to_dict()
        else:
            if self.bot.allowed_mentions is not None:
                allowed_mentions = self.bot.allowed_mentions.to_dict()
            else:
                allowed_mentions = {}

        base = {
            "content": content,
            "tts": tts,
            "embeds": [x.to_dict() for x in embeds] if embeds else [],
            "allowed_mentions": allowed_mentions,
            "components": components or [],
        }
        if hidden:
            base["flags"] = 64

        initial_message = False
        if not self.responded:
            initial_message = True
            if files and not self.deferred:
                await self.defer(hidden=hidden)
            if self.deferred:
                if self._deferred_hidden != hidden:
                    self._logger.warning(
                        "Deferred response might not be what you set it to! (hidden / visible) "
                        "This is because it was deferred in a different state."
                    )
                resp = await self._http.edit(base, self._token, files=files)
                self.deferred = False
            else:
                json_data = {"type": 4, "data": base}
                await self._http.post_initial_response(json_data, self.interaction_id, self._token)
                if not hidden:
                    resp = await self._http.edit({}, self._token)
                else:
                    resp = {}
            self.responded = True
        else:
            resp = await self._http.post_followup(base, self._token, files=files)
        if files:
            for file in files:
                file.close()
        if not hidden:
            try:
                self.menu_messages = (
                    self.data["resolved"]["messages"] if "resolved" in self.data.keys() else None
                )
            except:  # noqa
                self.menu_messages = None
            if self.menu_messages:
                smsg = Message(
                    state=self.bot._connection,
                    data=resp,
                    channel=self.channel or Object(id=self.channel_id),
                    _http=self._http,
                    interaction_token=self._token,
                )
            else:
                smsg = Message(
                    state=self.bot._connection,
                    data=resp,
                    channel=self.channel or Object(id=self.channel_id),
                    _http=self._http,
                    interaction_token=self._token,
                )
            if delete_after:
                self.bot.loop.create_task(smsg.delete(delay=delete_after))
            if initial_message:
                self.message = smsg
            return smsg
        else:
            return resp
    """