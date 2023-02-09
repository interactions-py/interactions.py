# versionadded is specified in docs gen file

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union

from ...client.enums import IntEnum
from ...utils.attrs_utils import ClientSerializerMixin, define, field
from ...utils.missing import MISSING
from ..error import LibraryException
from .misc import AllowedMentions, File, IDMixin, Image, Snowflake
from .user import User

if TYPE_CHECKING:
    from ...client.models.component import ActionRow, Button, SelectMenu
    from ..http import HTTPClient
    from .channel import Channel
    from .guild import Guild
    from .message import Attachment, Embed, Message

__all__ = (
    "Webhook",
    "WebhookType",
)


class WebhookType(IntEnum):
    Incoming = 1
    Channel_Follower = 2
    Application = 3


@define()
class Webhook(ClientSerializerMixin, IDMixin):
    """
    A class object representing a Webhook.

    :ivar Snowflake id: the id of the webhook
    :ivar WebhookType type: the type of the webhook
    :ivar Snowflake guild_id: the guild id this webhook is for, if any
    :ivar Snowflake channel_id: the channel id this webhook is for, if any
    :ivar User user: the user this webhook was created by (not returned when getting a webhook with its token)
    :ivar str name: the default name of the webhook
    :ivar str avatar: the default user avatar hash of the webhook
    :ivar str token: the secure token of the webhook (returned for Incoming Webhooks)
    :ivar Snowflake application_id: the bot/OAuth2 application that created this webhook
    :ivar Guild source_guild: the guild of the channel that this webhook is following (returned for Channel Follower Webhooks)
    :ivar Channel source_channel: the channel that this webhook is following (returned for Channel Follower Webhooks)
    :ivar str url: the url used for executing the webhook (returned by the webhooks OAuth2 flow)
    """

    id: Snowflake = field(converter=Snowflake)
    type: Union[WebhookType, int] = field(converter=WebhookType)
    guild_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    channel_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    user: Optional[User] = field(converter=User, default=None, add_client=True)
    name: str = field()
    avatar: str = field(repr=False)
    token: Optional[str] = field(default=None)
    application_id: Snowflake = field(converter=Snowflake)
    source_guild: Optional["Guild"] = field(default=None)
    source_channel: Optional["Channel"] = field(default=None)
    url: Optional[str] = field(default=None)

    def __attrs_post_init__(self):
        # circular imports suck
        from .channel import Channel
        from .guild import Guild

        self.source_guild = (
            Guild(**self.source_guild, _client=self._client) if self.source_guild else None
        )
        self.source_channel = (
            Channel(**self.source_channel, _client=self._client) if self.source_channel else None
        )

    @property
    def created_at(self) -> datetime:
        """
        .. versionadded:: 4.4.0

        Returns when the webhook was created.
        """
        return self.id.timestamp

    @classmethod
    async def create(
        cls,
        client: "HTTPClient",
        channel_id: int,
        name: str,
        avatar: Optional[Image] = MISSING,
    ) -> "Webhook":
        """
        Creates a webhook in a channel.

        :param HTTPClient client: The HTTPClient of the bot, has to be set to ``bot._http``.
        :param int channel_id: The ID of the channel to create the webhook in.
        :param str name: The name of the webhook.
        :param Optional[Image] avatar: The avatar of the Webhook, if any.
        :return: The created webhook as object
        :rtype: Webhook
        """

        _avatar = avatar.data if avatar is not MISSING else None

        res = await client.create_webhook(channel_id=channel_id, name=name, avatar=_avatar)

        return cls(**res, _client=client)

    @classmethod
    async def get(
        cls,
        client: "HTTPClient",
        webhook_id: int,
        webhook_token: Optional[str] = MISSING,
    ) -> "Webhook":
        """
        Gets an existing webhook.

        :param HTTPClient client: The HTTPClient of the bot, has to be set to ``bot._http``.
        :param int webhook_id: The ID of the webhook.
        :param Optional[str] webhook_token: The token of the webhook, optional
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
    ) -> "Webhook":  # sourcery skip: compare-via-equals
        """
        Modifies the current webhook.

        :param Optional[str] name: The new name of the webhook
        :param int channel_id: The channel id of the webhook. If not provided, the webhook token will be used for authentication
        :param Optional[Image] avatar: The new avatar of the webhook
        :return: The modified webhook object
        :rtype: Webhook
        """

        if not self._client:
            raise LibraryException(code=13)

        if channel_id in (None, MISSING) and not self.token:
            raise LibraryException(
                message="no token was found, please specify a channel id!", code=12
            )

        payload = {}

        if name is not MISSING:
            payload["name"] = name

        if avatar is not MISSING:
            payload["avatar"] = avatar.data

        if channel_id is not MISSING:
            payload["channel_id"] = channel_id

        res = await self._client.modify_webhook(
            webhook_id=int(self.id),
            payload=payload,
            webhook_token=None if channel_id else self.token,
        )

        self.update(res)
        return self

    async def execute(
        self,
        content: Optional[str] = MISSING,
        username: Optional[str] = MISSING,
        avatar_url: Optional[str] = MISSING,
        tts: Optional[bool] = MISSING,
        embeds: Optional[Union["Embed", List["Embed"]]] = MISSING,
        allowed_mentions: Optional[Union[AllowedMentions, dict]] = MISSING,
        attachments: Optional[List["Attachment"]] = MISSING,
        components: Optional[
            Union[
                "ActionRow",
                "Button",
                "SelectMenu",
                List["ActionRow"],
                List["Button"],
                List["SelectMenu"],
            ]
        ] = MISSING,
        files: Optional[Union[File, List[File]]] = MISSING,
        thread_id: Optional[int] = MISSING,
    ) -> Optional["Message"]:  # sourcery skip: low-code-quality
        """
        Executes the webhook. All parameters to this function are optional.

        .. important::
            The ``components`` argument requires an application-owned webhook.

        :param str content: the message contents (up to 2000 characters)
        :param str username: override the default username of the webhook
        :param str avatar_url: override the default avatar of the webhook
        :param bool tts: true if this is a TTS message
        :param Optional[List[Attachment]] attachments: The attachments to attach to the message. Needs to be uploaded to the CDN first
        :param Union[Embed, List[Embed]] embeds: embedded ``rich`` content
        :param Optional[Union[AllowedMentions, dict]] allowed_mentions: The allowed mentions for the message.
        :param Union[ActionRow, Button, SelectMenu, List[ActionRow], List[Button], List[SelectMenu]] components: the components to include with the message
        :param Union[File, List[File]] files: The files to attach to the message
        :param int thread_id: Send a message to a specified thread within a webhook's channel. The thread will automatically be unarchived
        :return: The sent message, if present
        :rtype: Optional[Message]
        """

        if not self._client:
            raise LibraryException(code=13)

        from ...client.models.component import _build_components
        from .message import Message

        _content: str = "" if content is MISSING else content
        _tts: bool = False if tts is MISSING else tts
        _attachments = [] if attachments is MISSING else [a._json for a in attachments]

        _embeds: list = (
            []
            if not embeds or embeds is MISSING
            else ([embed._json for embed in embeds] if isinstance(embeds, list) else [embeds._json])
        )
        _allowed_mentions: dict = (
            {}
            if allowed_mentions is MISSING
            else allowed_mentions._json
            if isinstance(allowed_mentions, AllowedMentions)
            else allowed_mentions
        )

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

        _files.extend(_attachments)

        payload: dict = dict(
            content=_content,
            tts=_tts,
            attachments=_files,
            embeds=_embeds,
            components=_components,
            allowed_mentions=_allowed_mentions,
        )

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

        return Message(**res, _client=self._client) if isinstance(res, dict) else res

    async def delete(self) -> None:
        """
        Deletes the webhook.
        """
        if not self._client:
            raise LibraryException(code=13)

        await self._client.delete_webhook(webhook_id=int(self.id), webhook_token=self.token)

    @property
    def avatar_url(self) -> Optional[str]:
        """
        Returns the URL of the webhook's avatar.

        :return: URL of the webhook's avatar
        :rtype: str
        """
        if not self.avatar:
            return None

        url = f"https://cdn.discordapp.com/avatars/{int(self.id)}/{self.avatar}"
        url += ".gif" if self.avatar.startswith("a_") else ".png"
        return url
