from typing import overload, Type, TypeVar, List, Iterable, Optional, Callable, Awaitable, Literal

from interactions.client.bot import Client
from enum import Enum
from ..api.models.channel import Channel
from ..api.models.guild import Guild
from ..api.models.member import Member
from ..api.models.message import Message, Emoji, Sticker
from ..api.models.user import User
from ..api.models.webhook import Webhook
from ..api.models.role import Role

_T = TypeVar("_T", Channel, Guild, Webhook, User, Sticker)
_P = TypeVar("_P", Member, Emoji, Role, Message)
_A = TypeVar("_A", Channel, Guild, Webhook, User, Sticker, Message, Emoji, Role, Message)

__all__: tuple

class Force(str, Enum):
    """
    An enum representing the force methods for the get method
    """
    CACHE: str
    HTTP: str

# not API-object related
@overload
def get(
    items: Iterable[_A], /, *, id: Optional[int] = None, name: Optional[str] = None, check: Callable[..., bool], **kwargs
) -> Optional[_A]: ...

# API-object related

# with http force
# single objects
@overload
def get(
    client: Client,
    obj: Type[_T],
    *,
    object_id: int,
    force: Optional[Literal["http", Force.HTTP]] = None
) -> Awaitable[_T]: ...

@overload
def get(
    client: Client,
    obj: Type[_P],
    *,
    parent_id: int,
    object_id: int,
    force: Optional[Literal["http", Force.HTTP]] = None
) -> Awaitable[_P]: ...

# list of objects
@overload
def get(
    client: Client,
    obj: Type[List[_T]],
    *,
    object_ids: List[int],
    force: Optional[Literal["http", Force.HTTP]] = None
) -> Awaitable[List[_T]]: ...

@overload
def get(
    client: Client,
    obj: Type[List[_P]],
    *,
    parent_id: int,
    object_ids: List[int],
    force: Optional[Literal["http", Force.HTTP]] = None
) -> Awaitable[List[_P]]: ...

# with cache force
@overload
def get(client: Client, obj: Type[_T], *, object_id: int, force: Literal["cache", Force.CACHE]) -> Optional[_T]: ...

@overload
def get(
    client: Client, obj: Type[_P], *, parent_id: int, object_id: int, force: Literal["cache", Force.CACHE]
) -> Optional[_P]: ...

# list of objects
@overload
def get(
    client: Client, obj: Type[List[_T]], *, object_ids: List[int], force: Literal["cache", Force.CACHE]
) -> List[Optional[_T]]: ...

@overload
def get(
    client: Client,
    obj: Type[List[_P]],
    *,
    parent_id: int,
    object_ids: List[int],
    force: Literal["cache", Force.CACHE]
) -> List[Optional[_P]]: ...

# Having a not-overloaded definition stops showing a warning/complaint from the IDE if wrong arguments are put in,
# so we'll leave that out

def _search_iterable(item: Iterable[_A], **kwargs) -> Optional[_A]:... 
def _get_cache(
    _object: Type[_A], client: Client, kwarg_name: str, _list: bool = False, **kwargs
) -> Union[Optional[_A], List[Optional[_A]]]:... 
async def _return_cache(
    obj: Union[Optional[_A], List[Optional[_A]]]
) -> Union[Optional[_A], List[Optional[_A]]]:... 
async def _http_request(
    obj: Type[_A],
    http: HTTPClient,
    request: Union[Coroutine, List[Union[_A, Coroutine]], List[Coroutine]] = None,
    _name: str = None,
    **kwargs,
) -> Union[_A, List[_A]]:... 

