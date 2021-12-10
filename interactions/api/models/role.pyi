from typing import Any, Optional

from .misc import DictSerializerMixin, Snowflake

class RoleTags(DictSerializerMixin):
    _json: dict
    bot_id: Optional[Snowflake]
    integration_id: Optional[Snowflake]
    premium_subscriber: Optional[Any]
    def __init__(self, **kwargs): ...

class Role(DictSerializerMixin):
    _json: dict
    id: Snowflake
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
    def __init__(self, **kwargs): ...
