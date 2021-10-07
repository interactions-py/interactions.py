from typing import List, Optional

from .misc import DictSerializerMixin
from .user import User

class TeamMember(DictSerializerMixin):
    _json: dict
    membership_state: int
    permissions: List[str]
    team_id: int
    user: User
    def __init__(self, **kwargs): ...

class Team(DictSerializerMixin):
    _json: dict
    icon: Optional[str]
    id: int
    members: List[TeamMember]
    name: str
    owner_user_id: int
    def __init__(self, **kwargs): ...

class Application(DictSerializerMixin):
    _json: dict
    id: int
    name: str
    icon: Optional[str]
    description: str
    rpc_origins: Optional[List[str]]
    bot_public: bool
    bot_require_code_grant: bool
    terms_of_service_url: Optional[str]
    privacy_policy_url: Optional[str]
    owner: Optional[User]
    summary: str
    verify_key: str
    team: Optional[Team]
    guild_id: Optional[int]
    primary_sku_id: Optional[int]
    slug: Optional[str]
    cover_image: Optional[str]
    flags: Optional[int]
    def __init__(self, **kwargs): ...
