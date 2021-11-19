from typing import Any, Optional

from .misc import DictSerializerMixin

class RoleTags(DictSerializerMixin):
    _json: dict
    bot_id: Optional[int]
    integration_id: Optional[int]
    premium_subscriber: Optional[Any]

    __slots__ = ("_json", "bot_id", "integration_id", "premium_subscriber")
    def __init__(self, **kwargs): ...

class Role(DictSerializerMixin):
    _json: dict
    id: int
    name: str
    color: int
    hoist: bool
    icon: Optional[str]
    unicode_emoji: Optional[str]
    position: int
    permissions: str
    managed: bool
    mentionable: bool
    tags: Optional[RoleTags]

    __slots__ = (
        "_json",
        "id",
        "name",
        "color",
        "hoist",
        "icon",
        "unicode_emoji",
        "position",
        "managed",
        "mentionable",
        "tags",
    )
    def __init__(self, **kwargs): ...
