from enum import IntEnum
from typing import Any, List, Optional, Union

from ..http.client import HTTPClient
from .channel import Channel
from .guild import Guild
from .message import Embed, Message
from .misc import MISSING, DictSerializerMixin, File, Image, Snowflake
from .user import User


class WebhookType(IntEnum):
    Incoming = 1
    Channel_Follower = 2
    Application = 3


class Webhook(DictSerializerMixin):
    """
    A class object representing a Webhook.

    :ivar Snowflake id: the id of the webhook
    :ivar WebhookType type: the type of the webhook
    :ivar Snowflake guild_id?: the guild id this webhook is for, if any
    :ivar Snowflake channel_id?: the channel id this webhook is for, if any
    :ivar User user?: the user this webhook was created by (not returned when getting a webhook with its token)
    :ivar str name: the default name of the webhook
    :ivar str avatar: the default user avatar hash of the webhook
    :ivar str token: the secure token of the webhook (returned for Incoming Webhooks)
    :ivar Snowflake application_id: the bot/OAuth2 application that created this webhook
    :ivar Guild source_guild?: the guild of the channel that this webhook is following (returned for Channel Follower Webhooks)
    :ivar Channel source_channel?: the channel that this webhook is following (returned for Channel Follower Webhooks)
    :ivar str url?: the url used for executing the webhook (returned by the webhooks OAuth2 flow)
    """

    __slots__ = (
        "_json",
        "_client",
        "id",
        "type",
        "guild_id",
        "channel_id",
        "user",
        "name",
        "avatar",
        "token",
        "application_id",
        "source_guild",
        "source_channel",
        "url",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.type = WebhookType(self.type) if self._json.get("type") else None
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.channel_id = Snowflake(self.channel_id) if self._json.get("channel_id") else None
        self.user = User(**self.user) if self._json.get("user") else None
        self.application_id = (
            Snowflake(self.application_id) if self._json.get("application_id") else None
        )
        self.source_guild = Guild(**self.source_guild) if self._json.get("source_guild") else None
        self.source_channel = (
            Channel(**self.source_channel) if self._json.get("source_channel") else None
        )

    @classmethod
    async def create(
        cls, client: HTTPClient, channel_id: int, name: str, avatar: Optional[Image] = MISSING
    ) -> "Webhook":
        """
        Creates a webhook in a channel.

        :param client: The HTTPClient of the bot, has to be set to `bot._http`.
        :type client: HTTPClient
        :param channel_id: The ID of the channel to create the webhook in.
        :type channel_id: int
        :param name: The name of the webhook.
        :type name: str
        :param avatar: The avatar of the Webhook, if any.
        :type avatar: Optional[Image]
        :return: The created webhook as object
        :rtype: Webhook
        """

        _avatar = avatar if avatar is not MISSING else None

        res = await client.create_webhook(channel_id=channel_id, name=name, avatar=_avatar)

        return cls(**res, _client=client)

    @classmethod
    async def get(
        cls, client: HTTPClient, webhook_id: int, webhook_token: Optional[str] = MISSING
    ) -> "Webhook":
        """
        Gets an existing webhook.

        :param client: The HTTPClient of the bot, has to be set to `bot._http`.
        :type client: HTTPClient
        :param webhook_id: The ID of the webhook.
        :type webhook_id: int
        :param webhook_token: The token of the webhook, optional
        :type webhook_token: Optional[str]
        :return: The Webhook object
        :rtype: Webhook
        """

        _token = webhook_token if webhook_token is not MISSING else None

        res = await client.get_webhook(webhook_id=webhook_id, webhook_token=_token)

        return cls(**res, _client=client)

    async def modify(
        self,
        name: Optional[str] = MISSING,
        channel_id: int = MISSING,
        avatar: Optional[Image] = MISSING,
    ) -> "Webhook":
        """
        Modifies the current webhook.

        :param name: The new name of the webhook
        :type name: Optional[str]
        :param channel_id: The channel id of the webhook. If not provided, the webhook token will be used for authentication
        :type channel_id: int
        :param avatar: The new avatar of the webhook
        :type avatar: Optional[Image]
        :return: The modified webhook object
        :rtype: Webhook
        """

        if not self._client:
            raise AttributeError("HTTPClient not found!")

        if channel_id in (None, MISSING) and not self.token:
            raise ValueError("no token was found, please specify a channel id!")

        payload = {}

        if name is not MISSING:
            payload["name"] = name

        if avatar is not MISSING:
            payload["avatar"] = avatar.data

        if not self.token:
            payload["channel_id"] = channel_id

        res = await self._client.modify_webhook(
            webhook_id=int(self.id),
            payload=payload,
            webhook_token=None if channel_id else self.token,
        )

        webhook = Webhook(**res, _client=self._client)

        for attr in self.__slots__:
            setattr(self, attr, getattr(webhook, attr))

        return webhook

    async def execute(
        self,
        content: Optional[str] = MISSING,
        username: Optional[str] = MISSING,
        avatar_url: Optional[str] = MISSING,
        tts: Optional[bool] = MISSING,
        embeds: Optional[Union[Embed, List[Embed]]] = MISSING,
        allowed_mentions: Any = MISSING,
        components: Optional[
            Union[
                "ActionRow",
                "Button",
                "SelectMenu",
                List["ActionRow"],
                List["Button"],
                List["SelectMenu"],
            ]  # noqa
        ] = MISSING,
        files: Optional[Union[File, List[File]]] = MISSING,
        thread_id: Optional[int] = MISSING,
    ) -> Message:
        """
        Executes the webhook. All parameters to this function are optional.

        .. important::
            The ``components`` argument requires an application-owned webhook.

        :param content: the message contents (up to 2000 characters)
        :type content: str
        :param username: override the default username of the webhook
        :type username: str
        :param avatar_url: override the default avatar of the webhook
        :type avatar_url: str
        :param tts: true if this is a TTS message
        :type tts: bool
        :param embeds: embedded ``rich`` content
        :type embeds: Union[Embed, List[Embed]]
        :param allowed_mentions: allowed mentions for the message
        :type allowed_mentions: dict
        :param components: the components to include with the message
        :type components: Union[ActionRow, Button, SelectMenu, List[ActionRow], List[Button], List[SelectMenu]]
        :param files: The files to attach to the message
        :type files: Union[File, List[File]]
        :param thread_id: Send a message to a specified thread within a webhook's channel. The thread will automatically be unarchived
        :type thread_id: int
        """

        if not self._client:
            raise AttributeError("HTTPClient not found!")

        from ...client.models.component import ActionRow, Button, SelectMenu, _build_components

        _content: str = "" if content is MISSING else content
        _tts: bool = False if tts is MISSING else tts
        # _attachments = [] if attachments else None
        _embeds: list = (
            []
            if not embeds or embeds is MISSING
            else ([embed._json for embed in embeds] if isinstance(embeds, list) else [embeds._json])
        )
        _allowed_mentions: dict = {} if allowed_mentions is MISSING else allowed_mentions

        if not components or components is MISSING:
            _components = []
        else:
            _components = _build_components(components=components)

        if not files or files is MISSING:
            _files = []
        elif isinstance(files, list):
            _files = [file._json_payload(id) for id, file in enumerate(files)]
        else:
            _files = [files._json_payload(0)]
            files = [files]

        msg = Message(
            content=_content,
            tts=_tts,
            attachments=_files,
            embeds=_embeds,
            components=_components,
            allowed_mentions=_allowed_mentions,
        )

        payload = msg._json

        if username is not MISSING:
            payload["username"] = username

        if avatar_url is not MISSING:
            payload["avatar_url"] = avatar_url

        res = await self._client.execute_webhook(
            webhook_id=int(self.id),
            webhook_token=self.token,
            files=files,
            payload=payload,
            thread_id=thread_id if thread_id is not MISSING else None,
        )

        return Message(**res, _client=self._client)

    @property
    def avatar_url(self) -> Optional[str]:
        """
        Returns the URL of the webhook's avatar

        :return: URL of the webhook's avatar.
        :rtype: str
        """
        if not self.avatar:
            return None

        url = f"https://cdn.discordapp.com/avatars/{int(self.id)}/{self.avatar}"
        url += ".gif" if self.avatar.startswith("a_") else ".png"
        return url
