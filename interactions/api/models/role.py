from typing import Optional


class RoleTags(object):
    bot_id: Optional[int]
    integration_id: Optional[int]
    premium_subscriber: Optional[int]

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Role(object):
    id: int
    name: str
    color: int
    hoist: bool
    position: int
    permissions: str
    managed: bool
    mentionable: bool
    tags: Optional[RoleTags]

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
