from .channel import ThreadMember
from .flags import AppFlags
from .misc import DictSerializerMixin, Snowflake
from .user import User


class TeamMember(DictSerializerMixin):
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

    __slots__ = ("_json", "membership_state", "permissions", "team_id", "user")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.team_id = Snowflake(self.team_id) if self._json.get("team_id") else None
        self.user = User(**self.user) if self._json.get("user") else None


class Team(DictSerializerMixin):
    """
    A class object representing a team.

    :ivar Optional[str] icon?: The hash of the team's icon
    :ivar Snowflake id: The team's unique ID
    :ivar List[TeamMember] members: The members of the team
    :ivar str name: The team name
    :ivar Snowflake owner_user_id: The User ID of the current team owner
    """

    __slots__ = ("_json", "icon", "id", "members", "name", "owner_user_id")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.owner_user_id = (
            Snowflake(self.owner_user_id) if self._json.get("owner_user_id") else None
        )
        self.members = (
            [ThreadMember(**member) for member in self.members]
            if self._json.get("members")
            else None
        )


class Application(DictSerializerMixin):
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

    __slots__ = (
        "_json",
        "id",
        "name",
        "icon",
        "description",
        "rpc_origins",
        "bot_public",
        "bot_require_code_grant",
        "terms_of_service_url",
        "privacy_policy_url",
        "owner",
        "summary",
        "verify_key",
        "team",
        "guild_id",
        "primary_sku_id",
        "slug",
        "cover_image",
        "flags",
        "type",
        "hook",
        "tags",  # TODO: document/investigate what it does.
        "install_params",
        "custom_install_url",
    )

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.primary_sku_id = (
            Snowflake(self.primary_sku_id) if self._json.get("primary_sku_id") else None
        )
        self.owner = User(**self.owner) if self._json.get("owner") else None
        self.team = Team(**self.team) if self._json.get("team") else None
        self.flags = AppFlags(self.flags) if self._json.get("flags") else None
