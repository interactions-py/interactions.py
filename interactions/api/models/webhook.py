from enum import IntEnum
from typing import Optional

from ..http.client import HTTPClient
from .channel import Channel
from .guild import Guild
from .misc import MISSING, DictSerializerMixin, Image, Snowflake
from .user import User


class WebhookType(IntEnum):
    Incoming = 1
    Channel_Follower = 2
    Application = 3


class Webhook(DictSerializerMixin):
    """
    A class object representing a Webhook.
    """

    __slots__ = (
        "_json",
        "_client" "id",
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

        return cls(**res)

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

        webhook = Webhook(**res)

        for attr in self.__slots__:
            setattr(self, attr, getattr(webhook, attr))

        return webhook

    @property
    def avatar_url(self) -> Optional[str]:
        """
        Returns the URL of the user's avatar

        :return: URL of the user's avatar.
        :rtype: str
        """
        if not self.avatar:
            return None

        url = f"https://cdn.discordapp.com/avatars/{int(self.id)}/{self.avatar}"
        url += ".gif" if self.avatar.startswith("a_") else ".png"
        return url
