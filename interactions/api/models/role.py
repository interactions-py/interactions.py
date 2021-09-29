from typing import Optional

from .misc import DictSerializerMixin


class RoleTags(DictSerializerMixin):
    _json: dict
    bot_id: Optional[int]
    integration_id: Optional[int]
    premium_subscriber: Optional[int]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
