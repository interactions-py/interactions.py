from typing import Optional

from orjson import dumps, loads


class RoleTags(object):
    _json: dict
    bot_id: Optional[int]
    integration_id: Optional[int]
    premium_subscriber: Optional[int]

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self._json = loads(dumps(self.__dict__))


class Role(object):
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
        self.__dict__.update(kwargs)
        self._json = loads(dumps(self.__dict__))
