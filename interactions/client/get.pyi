from typing import overload, Type, TypeVar, List, Iterable, Optional, Callable, Awaitable, Literal

from interactions.client.bot import Client
from enum import Enum
from interactions.api.models.channel import Channel
from interactions.api.models.guild import Guild
from interactions.api.models.member import Member
from interactions.api.models.message import Message, Emoji, Sticker
from interactions.api.models.role import Role
from interactions.api.models.user import User
from interactions.api.models.webhook import Webhook

_T = TypeVar("_T")

class Force(str, Enum):
    """
    An enum representing the force methods for the get method
    """
    CACHE: str
    HTTP: str

# not API-object related
@overload
def get(
    item: Iterable, *, id: Optional[int] = None, name: Optional[str] = None, check: Callable[..., bool]
) -> _T: ...

# API-object related

#with http force
# single objects
@overload
def get(client: Client, obj: Type[Channel], *, channel_id: int, force: Optional[Literal["http", Force.HTTP]] = None) -> Awaitable[Channel]: ...
@overload
def get(
    client: Client, obj: Type[Emoji], *, guild_id: int, emoji_id: int, force: Optional[Literal["http", Force.HTTP]] = None
) -> Awaitable[Emoji]: ...
@overload
def get(client: Client, obj: Type[Guild], *, guild_id: int, force: Optional[Literal["http", Force.HTTP]] = None) -> Awaitable[Guild]: ...
@overload
def get(
    client: Client, obj: Type[Member], *, guild_id: int, member_id: int, force: Optional[Literal["http", Force.HTTP]] = None
) -> Awaitable[Member]: ...
@overload
def get(
    client: Client,
    obj: Type[Message],
    *,
    channel_id: int,
    message_id: int,
    force: Optional[Literal["http"]] = None,
) -> Awaitable[Message]: ...
@overload
def get(client: Client, obj: Type[Role], *, guild_id: int, role_id: int, force: Optional[Literal["http", Force.HTTP]] = None) -> Awaitable[Role]: ...
@overload
def get(client: Client, obj: Type[Sticker], *, sticker_id: int, force: Optional[Literal["http", Force.HTTP]] = None) -> Awaitable[Sticker]: ...
@overload
def get(client: Client, obj: Type[User], *, user_id: int, force: Optional[Literal["http", Force.HTTP]] = None) -> Awaitable[User]: ...
@overload
def get(client: Client, obj: Type[Webhook], *, webhook_id: int, force: Optional[Literal["http", Force.HTTP]] = None) -> Awaitable[Webhook]: ...

# list of objects
@overload
def get(client: Client, obj: Type[List[Channel]], *, channel_ids: List[int], force: Optional[Literal["http", Force.HTTP]] = None) -> Awaitable[List[Channel]]: ...
@overload
def get(client: Client, obj: Type[List[Emoji]], *, guild_id: int, emoji_ids: List[int], force: Optional[Literal["http", Force.HTTP]] = None) -> Awaitable[List[Emoji]]: ...
@overload
def get(client: Client, obj: Type[List[Guild]], *, guild_ids: List[int], force: Optional[Literal["http", Force.HTTP]] = None) -> Awaitable[List[Guild]]: ...
@overload
def get(
    client: Client,
    obj: Type[List[Member]],
    *,
    guild_id: int,
    member_ids: List[int],
    force: Optional[Literal["http", Force.HTTP]] = None
) -> Awaitable[List[Member]]: ...
@overload
def get(
    client: Client,
    obj: Type[List[Message]],
    *,
    channel_id: int,
    message_ids: List[int],
    force: Optional[Literal["http", Force.HTTP]] = None
) -> Awaitable[List[Message]]: ...
@overload
def get(client: Client, obj: Type[List[Role]], *, guild_id: int, role_ids: List[int], force: Optional[Literal["http", Force.HTTP]] = None) -> Awaitable[List[Role]]: ...
@overload
def get(client: Client, obj: Type[List[Sticker]], *, sticker_ids: List[int], force: Optional[Literal["http", Force.HTTP]] = None) -> Awaitable[List[Sticker]]: ...
@overload
def get(client: Client, obj: Type[List[User]], *, user_ids: List[int], force: Optional[Literal["http", Force.HTTP]] = None) -> Awaitable[List[User]]: ...
@overload
def get(client: Client, obj: Type[List[Webhook]], *, webhook_ids: List[int], force: Optional[Literal["http", Force.HTTP]] = None) -> Awaitable[List[Webhook]]: ...

# with cache force
@overload
def get(client: Client, obj: Type[Channel], *, channel_id: int, force: Literal["cache", Force.CACHE]) -> Channel: ...
@overload
def get(
    client: Client, obj: Type[Emoji], *, guild_id: int, emoji_id: int, force: Literal["cache", Force.CACHE]
) -> Emoji: ...
@overload
def get(client: Client, obj: Type[Guild], *, guild_id: int, force: Literal["cache", Force.CACHE]) -> Guild: ...
@overload
def get(
    client: Client, obj: Type[Member], *, guild_id: int, member_id: int, force: Literal["cache", Force.CACHE]
) -> Member: ...
@overload
def get(
    client: Client,
    obj: Type[Message],
    *,
    channel_id: int,
    message_id: int,
    force: Literal["cache", Force.CACHE],
) -> Message: ...
@overload
def get(client: Client, obj: Type[Role], *, guild_id: int, role_id: int, force: Literal["cache", Force.CACHE]) -> Role: ...
@overload
def get(client: Client, obj: Type[Sticker], *, sticker_id: int, force: Literal["cache", Force.CACHE]) -> Sticker: ...
@overload
def get(client: Client, obj: Type[User], *, user_id: int, force: Literal["cache", Force.CACHE]) -> User: ...
@overload
def get(client: Client, obj: Type[Webhook], *, webhook_id: int, force: Literal["cache", Force.CACHE]) -> Webhook: ...

# list of objects
@overload
def get(client: Client, obj: Type[List[Channel]], *, channel_ids: List[int], force: Literal["cache", Force.CACHE]) -> List[Channel]: ...
@overload
def get(client: Client, obj: Type[List[Emoji]], *, guild_id: int, emoji_ids: List[int], force: Literal["cache", Force.CACHE]) -> List[Emoji]: ...
@overload
def get(client: Client, obj: Type[List[Guild]], *, guild_ids: List[int], force: Literal["cache", Force.CACHE]) -> List[Guild]: ...
@overload
def get(
    client: Client,
    obj: Type[List[Member]],
    *,
    guild_id: int,
    member_ids: List[int],
    force: Literal["cache", Force.CACHE]
) -> List[Member]: ...
@overload
def get(
    client: Client,
    obj: Type[List[Message]],
    *,
    channel_id: int,
    message_ids: List[int],
    force: Literal["cache", Force.CACHE]
) -> List[Message]: ...
@overload
def get(client: Client, obj: Type[List[Role]], *, guild_id: int, role_ids: List[int], force: Literal["cache", Force.CACHE]) -> List[Role]: ...
@overload
def get(client: Client, obj: Type[List[Sticker]], *, sticker_ids: List[int], force: Literal["cache", Force.CACHE]) -> List[Sticker]: ...
@overload
def get(client: Client, obj: Type[List[User]], *, user_ids: List[int], force: Literal["cache", Force.CACHE]) -> List[User]: ...
@overload
def get(client: Client, obj: Type[List[Webhook]], *, webhook_ids: List[int], force: Literal["cache", Force.CACHE]) -> List[Webhook]: ...

# Having a not-overloaded definition stops showing a warning/complaint from the IDE if wrong arguments are put in,
# so we'll leave that out
