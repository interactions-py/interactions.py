from .misc import DictSerializerMixin


class TeamMember(DictSerializerMixin):
    """
    The team member object.

    ..note::
        The membership state is either a 1 for invited, or 2 for accepted.
        At the moment, permissions will always be ["*"].

    :ivar int membership_state: The user's membership state on the team
    :ivar typing.List[str] permissions: Team Member permissions
    :ivar int team_id: ID of the team that they're a member of.
    :ivar User user: The user object.
    """

    __slots__ = ("_json", "membership_state", "permissions", "team_id", "user")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Team(DictSerializerMixin):
    """
    The team object.

    :ivar typing.Optional[str] icon: The hash of the team's icon
    :ivar int id: The team's unique ID
    :ivar typing.List[TeamMember] members: The members of the team
    :ivar str name: The team name
    :ivar int owner_user_id: The User ID of the current team owner
    """

    __slots__ = ("_json", "icon", "id", "members", "name", "owner_user_id")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Application(DictSerializerMixin):
    """
    The application object.

    ..note::
        Type and Hook are currently undocumented in the API.

    :ivar int id: Application ID
    :ivar str name: Application Name
    :ivar typing.Optional[str] icon: Icon hash of the application
    :ivar str description: Application Description
    :ivar typing.Optional[typing.List[str]] rpc_origins: An array of rpc origin urls, if RPC is used.
    :ivar bool bot_public: A status denoting if anyone can invite the bot to guilds
    :ivar bool bot_require_code_grant: A status denoting whether full Oauth2 is required for the app's bot to join a guild
    :ivar typing.Optional[str] terms_of_service_url: URL of the app's Terms of Service
    :ivar typing.Optional[str] privacy_policy_url: URL of the app's Privacy Policy
    :ivar Optional[User] owner: User object of the owner
    :ivar str summary: Summary of the store page, if this application is a game sold on Discord
    :ivar str verify_key: Hex encoded key for verification in interactions and/or the GameSDK's GetTicket
    :ivar typing.Optional[Team] team: A list of team members, if this app belongs to a team.
    :ivar typing.Optional[int] guild_id: Guild ID linked, if this app is a game sold on Discord
    :ivar typing.Optional[int] primary_sku_id: Game SKU ID, if this app is a game sold on Discord
    :ivar typing.Optional[str] slug: URL slug that links to the store page, if this app is a game sold on Discord
    :ivar typing.Optional[str] cover_image: The app's default rich presence invite cover image
    :ivar typing.Optional[int] flags: The application's public flags

    :ivar typing.Optional[typing.Any] type: Type of application(?)
    :ivar typing.Optional[typing.Any] hook: ?
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
    )

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
