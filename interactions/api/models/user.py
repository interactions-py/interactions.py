from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union

from ...utils.attrs_utils import ClientSerializerMixin, define, field
from ...utils.missing import MISSING
from ..error import LibraryException
from .flags import UserFlags
from .misc import AllowedMentions, File, IDMixin, Snowflake

if TYPE_CHECKING:
    from ...client.models.component import ActionRow, Button, SelectMenu
    from .channel import Channel
    from .gw import Presence
    from .message import Attachment, Embed, Message

__all__ = ("User",)


@define()
class User(ClientSerializerMixin, IDMixin):
    """
    A class object representing a user.

    :ivar Snowflake id: The User ID
    :ivar str username: The Username associated (not necessarily unique across the platform)
    :ivar str discriminator: The User's 4-digit discord-tag (i.e.: XXXX)
    :ivar Optional[str] avatar: The user's avatar hash, if any
    :ivar Optional[bool] bot: A status denoting if the user is a bot
    :ivar Optional[bool] system: A status denoting if the user is an Official Discord System user
    :ivar Optional[bool] mfa_enabled: A status denoting if the user has 2fa on their account
    :ivar Optional[str] banner: The user's banner hash, if any
    :ivar Optional[str] banner_color: The user's banner color as a hex, if any
    :ivar Optional[int] accent_color: The user's banner color as an integer represented of hex color codes
    :ivar Optional[str] locale: The user's chosen language option
    :ivar Optional[bool] verified: Whether the email associated with this account has been verified
    :ivar Optional[str] email: The user's email, if any
    :ivar Optional[UserFlags] flags: The user's flags
    :ivar Optional[int] premium_type: The type of Nitro subscription the user has
    :ivar Optional[UserFlags] public_flags: The user's public flags
    """

    id: Snowflake = field(converter=Snowflake)
    username: str = field(repr=True)
    discriminator: str = field(repr=True)
    avatar: Optional[str] = field(default=None, repr=False)
    bot: Optional[bool] = field(default=None)
    system: Optional[bool] = field(default=None, repr=False)
    mfa_enabled: Optional[bool] = field(default=None)
    banner: Optional[str] = field(default=None, repr=False)
    accent_color: Optional[int] = field(default=None, repr=False)
    banner_color: Optional[str] = field(default=None, repr=False)
    locale: Optional[str] = field(default=None)
    verified: Optional[bool] = field(default=None)
    email: Optional[str] = field(default=None)
    flags: Optional[UserFlags] = field(converter=UserFlags, default=None, repr=False)
    premium_type: Optional[int] = field(default=None, repr=False)
    public_flags: Optional[UserFlags] = field(converter=UserFlags, default=None, repr=False)
    bio: Optional[str] = field(default=None)

    def has_public_flag(self, flag: Union[UserFlags, int]) -> bool:
        """
        .. versionadded:: 4.3.0

        Returns whether the user has public flag.
        """
        if self.public_flags == 0 or self.public_flags is None:
            return False
        return bool(int(self.public_flags) & flag)

    @property
    def mention(self) -> str:
        """
        .. versionadded:: 4.1.0

        Returns a string that allows you to mention the given user.

        :return: The string of the mentioned user.
        :rtype: str
        """
        return f"<@{self.id}>"

    @property
    def avatar_url(self) -> str:
        """
        .. versionadded:: 4.2.0

        Returns the URL of the user's avatar

        :return: URL of the user's avatar.
        :rtype: str
        """
        url = "https://cdn.discordapp.com/"
        if self.avatar:
            url += f"avatars/{int(self.id)}/{self.avatar}"
            url += ".gif" if self.avatar.startswith("a_") else ".png"
        else:
            url += f"embed/avatars/{int(self.discriminator) % 5}.png"
        return url

    @property
    def banner_url(self) -> Optional[str]:
        """
        .. versionadded:: 4.2.0

        Returns the URL of the user's banner.

        :return: URL of the user's banner (None will be returned if no banner is set)
        :rtype: str
        """
        if not self.banner:
            return None

        url = f"https://cdn.discordapp.com/banners/{int(self.id)}/{self.banner}"
        url += ".gif" if self.banner.startswith("a_") else ".png"
        return url

    @property
    def presence(self) -> Optional["Presence"]:
        """
        .. versionadded:: 4.3.2

        Returns the presence of the user.

        :return: Presence of the user (None will be returned if not cached)
        :rtype: Optional[Presence]
        """
        from .gw import Presence

        return self._client.cache[Presence].get(self.id)

    @property
    def created_at(self) -> datetime:
        """
        .. versionadded:: 4.4.0

        Returns when the user was created.
        """
        return self.id.timestamp

    async def send(
        self,
        content: Optional[str] = MISSING,
        *,
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
        tts: Optional[bool] = MISSING,
        attachments: Optional[List["Attachment"]] = MISSING,
        files: Optional[Union[File, List[File]]] = MISSING,
        embeds: Optional[Union["Embed", List["Embed"]]] = MISSING,
        allowed_mentions: Optional[Union[AllowedMentions, dict]] = MISSING,
    ) -> "Message":
        """
        .. versionadded:: 4.3.2

        Sends a DM to the user.

        :param Optional[str] content: The contents of the message as a string or string-converted value.
        :param Optional[Union[ActionRow, Button, SelectMenu, List[ActionRow], List[Button], List[SelectMenu]]] components: A component, or list of components for the message.
        :param Optional[bool] tts: Whether the message utilizes the text-to-speech Discord programme or not.
        :param Optional[List[Attachment]] attachments: The attachments to attach to the message. Needs to be uploaded to the CDN first
        :param Optional[Union[File, List[File]]] files: A file or list of files to be attached to the message.
        :param Optional[Union[Embed, List[Embed]]] embeds: An embed, or list of embeds for the message.
        :param Optional[Union[AllowedMentions, dict]] allowed_mentions: The allowed mentions for the message.
        :return: The sent message as an object.
        :rtype: Message
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

        payload = dict(
            content=_content,
            tts=_tts,
            attachments=_files,
            embeds=_embeds,
            components=_components,
            allowed_mentions=_allowed_mentions,
        )
        channel = await self._client.create_dm(recipient_id=int(self.id))
        res = await self._client.create_message(
            channel_id=int(channel["id"]), payload=payload, files=files
        )

        return Message(**res, _client=self._client)

    async def get_dm_channel(self) -> "Channel":
        """
        .. versionadded:: 4.4.0

        Gets the DM channel with the user

        :return: The DM channel with the user
        :rtype: Channel
        """
        if not self._client:
            raise LibraryException(code=13)

        from .channel import Channel

        return Channel(**await self._client.create_dm(int(self.id)), _client=self._client)
