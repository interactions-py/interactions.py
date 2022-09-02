from typing import Any, List, Optional

from ...utils.attrs_utils import ClientSerializerMixin, convert_list, define, field
from .flags import AppFlags
from .misc import IDMixin, Snowflake
from .user import User

__all__ = (
    "Team",
    "TeamMember",
    "Application",
)


@define()
class TeamMember(ClientSerializerMixin):
    """
    A class object representing the member of a team.

    .. note::
        The membership state is either a 1 for invited, or 2 for accepted.
        At the moment, permissions will always be ["*"].

    :ivar int membership_state: The user's membership state on the team
    :ivar List[str] permissions: Team Member permissions
    :ivar Snowflake team_id: ID of the team that they're a member of.
    :ivar User user: The user object.
    """

    membership_state: int = field()
    permissions: List[str] = field()
    team_id: Snowflake = field(converter=Snowflake)
    user: User = field(converter=User, add_client=True)


@define()
class Team(ClientSerializerMixin, IDMixin):
    """
    A class object representing a team.

    :ivar Optional[str] icon?: The hash of the team's icon
    :ivar Snowflake id: The team's unique ID
    :ivar List[TeamMember] members: The members of the team
    :ivar str name: The team name
    :ivar Snowflake owner_user_id: The User ID of the current team owner
    """

    icon: Optional[str] = field(default=None)
    id: Snowflake = field(converter=Snowflake)
    members: List[TeamMember] = field(converter=convert_list(TeamMember), add_client=True)
    name: str = field()
    owner_user_id: int = field()


@define()
class Application(ClientSerializerMixin, IDMixin):
    """
    A class object representing an application.

    .. note::
        ``type`` and ``hook`` are currently undocumented in the API.

    :ivar Snowflake id: Application ID
    :ivar str name: Application Name
    :ivar Optional[str] icon?: Icon hash of the application
    :ivar str description: Application Description
    :ivar Optional[List[str]] rpc_origins?: An array of rpc origin urls, if RPC is used.
    :ivar bool bot_public: A status denoting if anyone can invite the bot to guilds
    :ivar bool bot_require_code_grant: A status denoting whether full Oauth2 is required for the app's bot to join a guild
    :ivar Optional[str] terms_of_service_url?: URL of the app's Terms of Service
    :ivar Optional[str] privacy_policy_url?: URL of the app's Privacy Policy
    :ivar Optional[User] owner?: User object of the owner
    :ivar str summary: Summary of the store page, if this application is a game sold on Discord
    :ivar str verify_key: Hex encoded key for verification in interactions and/or the GameSDK's GetTicket
    :ivar Optional[Team] team?: A list of team members, if this app belongs to a team.
    :ivar Optional[Snowflake] guild_id?: Guild ID linked, if this app is a game sold on Discord
    :ivar Optional[int] primary_sku_id?: Game SKU ID, if this app is a game sold on Discord
    :ivar Optional[str] slug?: URL slug that links to the store page, if this app is a game sold on Discord
    :ivar Optional[str] cover_image?: The app's default rich presence invite cover image
    :ivar Optional[AppFlags] flags?: The application's public flags
    """

    id: Snowflake = field(converter=Snowflake)
    name: str = field()
    icon: Optional[str] = field(default=None, repr=False)
    description: str = field()
    rpc_origins: Optional[List[str]] = field(default=None)
    bot_public: bool = field()
    bot_require_code_grant: bool = field()
    terms_of_service_url: Optional[str] = field(default=None)
    privacy_policy_url: Optional[str] = field(default=None)
    owner: Optional[User] = field(converter=User, default=None, add_client=True)
    summary: str = field()
    verify_key: str = field()
    team: Optional[Team] = field(converter=Team, default=None, add_client=True)
    guild_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    primary_sku_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    slug: Optional[str] = field(default=None)
    cover_image: Optional[str] = field(default=None, repr=False)
    flags: Optional[AppFlags] = field(converter=AppFlags, default=None)
    type: Optional[Any] = field(default=None)
    hook: Optional[Any] = field(default=None)

    @property
    def icon_url(self) -> Optional[str]:
        """
        Returns the URL of the application's icon

        :return: URL of the application's icon.
        :rtype: str (None will be returned if none of any icon is set)
        """
        url = "https://cdn.discordapp.com/"
        if self.icon:
            url += f"app-icons/{int(self.id)}/{self.icon}.png"
        else:
            url = None
        return url
