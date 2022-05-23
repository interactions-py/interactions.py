from typing import Any, List, Optional

from .attrs_utils import ClientSerializerMixin, define
from .flags import AppFlags as AppFlags
from .misc import Snowflake
from .user import User as User


@define()
class TeamMember(ClientSerializerMixin):
    membership_state: int
    permissions: List[str]
    team_id: Snowflake
    user: User


@define()
class Team(ClientSerializerMixin):
    icon: Optional[str]
    id: Snowflake
    members: List[TeamMember]
    name: str
    owner_user_id: int


@define()
class Application(ClientSerializerMixin):
    id: Snowflake
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
    guild_id: Optional[Snowflake]
    primary_sku_id: Optional[Snowflake]
    slug: Optional[str]
    cover_image: Optional[str]
    flags: Optional[AppFlags]
    type: Optional[Any]
    hook: Optional[Any]
    @property
    def icon_url(self) -> str: ...
