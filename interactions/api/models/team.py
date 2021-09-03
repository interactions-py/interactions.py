from typing import List, Optional

from .user import User


class TeamMember(object):
    membership_state: int
    permissions: List[str]
    team_id: int
    user: User


class Team(object):
    icon: Optional[str]
    id: int
    members: List[TeamMember]
    name: str
    owner_user_id: int


class Application(object):
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
