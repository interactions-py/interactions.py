from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union

from ...utils.attrs_utils import ClientSerializerMixin, convert_list, define, field
from ...utils.missing import MISSING
from ..error import LibraryException
from .misc import Snowflake
from .role import Role
from .user import User

if TYPE_CHECKING:
    from ..http import HTTPClient
    from .guild import Guild

__all__ = ("Emoji",)


@define()
class Emoji(ClientSerializerMixin):
    """
    A class objecting representing an emoji.

    :ivar Optional[Snowflake] id: Emoji id
    :ivar Optional[str] name: Emoji name.
    :ivar Optional[List[int]] roles: Roles allowed to use this emoji
    :ivar Optional[User] user: User that created this emoji
    :ivar Optional[bool] require_colons: Status denoting of this emoji must be wrapped in colons
    :ivar Optional[bool] managed: Status denoting if this emoji is managed (by an integration)
    :ivar Optional[bool] animated: Status denoting if this emoji is animated
    :ivar Optional[bool] available: Status denoting if this emoji can be used. (Can be false via server boosting)
    """

    id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    name: Optional[str] = field(default=None)
    roles: Optional[List[int]] = field(converter=convert_list(int), default=None)
    user: Optional[User] = field(converter=User, default=None)
    require_colons: Optional[bool] = field(default=None)
    managed: Optional[bool] = field(default=None)
    animated: Optional[bool] = field(default=None)
    available: Optional[bool] = field(default=None)

    @property
    def format(self) -> str:
        """
        .. versionadded:: 4.4.0

        Formats the emoji into a send-able form.

        :rtype: str
        """
        return (
            f"<{'a' if self.animated else ''}:{self.name}:{self.id}>"
            if self.id is not None
            else f":{self.name}:"
            if self.require_colons
            else self.name
        )

    @property
    def created_at(self) -> datetime:
        """
        .. versionadded:: 4.4.0

        Returns when the emoji was created.
        """
        return self.id.timestamp

    @classmethod
    async def get(
        cls,
        guild_id: Union[int, Snowflake, "Guild"],
        emoji_id: Union[int, Snowflake],
        client: "HTTPClient",
    ) -> "Emoji":
        """
        .. versionadded:: 4.2.0

        Gets an emoji.

        :param Union[int, Snowflake, Guild] guild_id: The id of the guild of the emoji
        :param Union[int, Snowflake] emoji_id: The id of the emoji
        :param HTTPClient client: The HTTPClient of your bot. Equals to ``bot._http``
        :return: The Emoji as object
        :rtype: Emoji
        """

        _guild_id = int(guild_id) if isinstance(guild_id, (int, Snowflake)) else int(guild_id.id)

        res = await client.get_guild_emoji(guild_id=_guild_id, emoji_id=int(emoji_id))
        return cls(**res, _client=client)

    @classmethod
    async def get_all_of_guild(
        cls,
        guild_id: Union[int, Snowflake, "Guild"],
        client: "HTTPClient",
    ) -> List["Emoji"]:
        """
        .. versionadded:: 4.2.0

        Gets all emoji of a guild.

        :param Union[int, Snowflake, Guild] guild_id: The id of the guild to get the emojis of
        :param HTTPClient client: The HTTPClient of your bot. Equals to ``bot._http``
        :return: The Emoji as list
        :rtype: List[Emoji]
        """

        _guild_id = int(guild_id) if isinstance(guild_id, (int, Snowflake)) else int(guild_id.id)

        res = await client.get_all_emoji(guild_id=_guild_id)
        return [cls(**emoji, _client=client) for emoji in res]

    async def modify(
        self,
        guild_id: Union[int, Snowflake, "Guild"],
        name: Optional[str] = MISSING,
        roles: Optional[Union[List[Role], List[int]]] = MISSING,
        reason: Optional[str] = None,
    ) -> "Emoji":
        """
        .. versionadded:: 4.4.0

        Edits the Emoji in a guild.

        :param int guild_id: The id of the guild to edit the emoji on
        :param Optional[str] name: The name of the emoji. If not specified, the filename will be used
        :param Optional[Union[List[Role], List[int]]] roles: Roles allowed to use this emoji
        :param Optional[str] reason: The reason of the modification
        :return: The modified emoji object
        :rtype: Emoji
        """
        if not self._client:
            raise LibraryException(code=13)

        payload: dict = {}

        if name is not MISSING:
            payload["name"] = name

        if roles is not MISSING:
            payload["roles"] = [int(role.id if isinstance(role, Role) else role) for role in roles]

        _guild_id = int(guild_id) if isinstance(guild_id, (int, Snowflake)) else int(guild_id.id)

        res = await self._client.modify_guild_emoji(
            guild_id=_guild_id, emoji_id=int(self.id), payload=payload, reason=reason
        )

        self.update(res)

        return self

    async def delete(
        self,
        guild_id: Union[int, Snowflake, "Guild"],
        reason: Optional[str] = None,
    ) -> None:
        """
        .. versionadded:: 4.2.0

        Deletes the emoji.

        :param Union[int, Snowflake, Guild] guild_id: The guild id to delete the emoji from
        :param Optional[str] reason: The reason for the deletion
        """
        if not self._client:
            raise LibraryException(code=13)

        _guild_id = int(guild_id) if isinstance(guild_id, (int, Snowflake)) else int(guild_id.id)

        return await self._client.delete_guild_emoji(
            guild_id=_guild_id, emoji_id=int(self.id), reason=reason
        )

    @property
    def url(self) -> str:
        """
        .. versionadded:: 4.2.0

        Returns the emoji's URL.

        :return: URL of the emoji
        :rtype: str
        """
        url = f"https://cdn.discordapp.com/emojis/{self.id}"
        url += ".gif" if self.animated else ".png"
        return url
