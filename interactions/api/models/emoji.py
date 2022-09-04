from typing import TYPE_CHECKING, List, Optional, Union

from ...utils.attrs_utils import ClientSerializerMixin, convert_list, define, field
from ..error import LibraryException
from .misc import Snowflake
from .user import User

if TYPE_CHECKING:
    from ..http import HTTPClient
    from .guild import Guild

__all__ = ("Emoji",)


@define(repr=False)
class Emoji(ClientSerializerMixin):
    """
    A class objecting representing an emoji.

    :ivar Optional[Snowflake] id?: Emoji id
    :ivar Optional[str] name?: Emoji name.
    :ivar Optional[List[int]] roles?: Roles allowed to use this emoji
    :ivar Optional[User] user?: User that created this emoji
    :ivar Optional[bool] require_colons?: Status denoting of this emoji must be wrapped in colons
    :ivar Optional[bool] managed?: Status denoting if this emoji is managed (by an integration)
    :ivar Optional[bool] animated?: Status denoting if this emoji is animated
    :ivar Optional[bool] available?: Status denoting if this emoji can be used. (Can be false via server boosting)
    """

    id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    name: Optional[str] = field(default=None)
    roles: Optional[List[int]] = field(converter=convert_list(int), default=None)
    user: Optional[User] = field(converter=User, default=None)
    require_colons: Optional[bool] = field(default=None)
    managed: Optional[bool] = field(default=None)
    animated: Optional[bool] = field(default=None)
    available: Optional[bool] = field(default=None)

    def __repr__(self):
        return (
            f"<{'a' if self.animated else ''}:{self.name}:{self.id}>"
            if self.id is not None
            else self.name
        )

    @classmethod
    async def get(
        cls,
        guild_id: Union[int, Snowflake, "Guild"],
        emoji_id: Union[int, Snowflake],
        client: "HTTPClient",
    ) -> "Emoji":
        """
        Gets an emoji.

        :param guild_id: The id of the guild of the emoji
        :type guild_id: Union[int, Snowflake, "Guild"]
        :param emoji_id: The id of the emoji
        :type emoji_id: Union[int, Snowflake]
        :param client: The HTTPClient of your bot. Equals to ``bot._http``
        :type client: HTTPClient
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
        Gets all emoji of a guild.

        :param guild_id: The id of the guild to get the emojis of
        :type guild_id: Union[int, Snowflake, "Guild"]
        :param client: The HTTPClient of your bot. Equals to ``bot._http``
        :type client: HTTPClient
        :return: The Emoji as list
        :rtype: List[Emoji]
        """

        _guild_id = int(guild_id) if isinstance(guild_id, (int, Snowflake)) else int(guild_id.id)

        res = await client.get_all_emoji(guild_id=_guild_id)
        return [cls(**emoji, _client=client) for emoji in res]

    async def delete(
        self,
        guild_id: Union[int, Snowflake, "Guild"],
        reason: Optional[str] = None,
    ) -> None:
        """
        Deletes the emoji.

        :param guild_id: The guild id to delete the emoji from
        :type guild_id: Union[int, Snowflake, "Guild"]
        :param reason?: The reason of the deletion
        :type reason?: Optional[str]
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
        Returns the emoji's URL.

        :return: URL of the emoji
        :rtype: str
        """
        url = f"https://cdn.discordapp.com/emojis/{self.id}"
        url += ".gif" if self.animated else ".png"
        return url
