from enum import IntFlag

from ...client.enums import StrEnum

__all__ = (
    "Intents",
    "AppFlags",
    "StatusType",
    "UserFlags",
    "Permissions",
    "MessageFlags",
    "MemberFlags",
)


class Intents(IntFlag):
    """An integer flag bitshift object representing flags respective for each gateway intent type."""

    GUILDS = 1 << 0
    GUILD_MEMBERS = 1 << 1
    GUILD_BANS = 1 << 2
    GUILD_EMOJIS_AND_STICKERS = 1 << 3
    GUILD_INTEGRATIONS = 1 << 4
    GUILD_WEBHOOKS = 1 << 5
    GUILD_INVITES = 1 << 6
    GUILD_VOICE_STATES = 1 << 7
    GUILD_PRESENCES = 1 << 8
    GUILD_MESSAGES = 1 << 9
    GUILD_MESSAGE_REACTIONS = 1 << 10
    GUILD_MESSAGE_TYPING = 1 << 11
    DIRECT_MESSAGES = 1 << 12
    DIRECT_MESSAGE_REACTIONS = 1 << 13
    DIRECT_MESSAGE_TYPING = 1 << 14
    GUILD_MESSAGE_CONTENT = 1 << 15
    GUILD_SCHEDULED_EVENTS = 1 << 16
    AUTO_MODERATION_CONFIGURATION = 1 << 20
    AUTO_MODERATION_EXECUTION = 1 << 21

    PRIVILEGED = GUILD_PRESENCES | GUILD_MEMBERS | GUILD_MESSAGE_CONTENT
    DEFAULT = (
        GUILDS
        | GUILD_BANS
        | GUILD_EMOJIS_AND_STICKERS
        | GUILD_INTEGRATIONS
        | GUILD_WEBHOOKS
        | GUILD_INVITES
        | GUILD_VOICE_STATES
        | GUILD_MESSAGES
        | GUILD_MESSAGE_REACTIONS
        | GUILD_MESSAGE_TYPING
        | DIRECT_MESSAGES
        | DIRECT_MESSAGE_REACTIONS
        | DIRECT_MESSAGE_TYPING
        | GUILD_SCHEDULED_EVENTS
        | AUTO_MODERATION_CONFIGURATION
        | AUTO_MODERATION_EXECUTION
    )
    ALL = DEFAULT | PRIVILEGED


class Permissions(IntFlag):
    """An integer flag bitshift object representing the different member permissions given by Discord."""

    CREATE_INSTANT_INVITE = 1 << 0
    KICK_MEMBERS = 1 << 1
    BAN_MEMBERS = 1 << 2
    ADMINISTRATOR = 1 << 3
    MANAGE_CHANNELS = 1 << 4
    MANAGE_GUILD = 1 << 5
    ADD_REACTIONS = 1 << 6
    VIEW_AUDIT_LOG = 1 << 7
    PRIORITY_SPEAKER = 1 << 8
    STREAM = 1 << 9
    VIEW_CHANNEL = 1 << 10
    SEND_MESSAGES = 1 << 11
    SEND_TTS_MESSAGES = 1 << 12
    MANAGE_MESSAGES = 1 << 13
    EMBED_LINKS = 1 << 14
    ATTACH_FILES = 1 << 15
    READ_MESSAGE_HISTORY = 1 << 16
    MENTION_EVERYONE = 1 << 17
    USE_EXTERNAL_EMOJIS = 1 << 18
    VIEW_GUILD_INSIGHTS = 1 << 19
    CONNECT = 1 << 20
    SPEAK = 1 << 21
    MUTE_MEMBERS = 1 << 22
    DEAFEN_MEMBERS = 1 << 23
    MOVE_MEMBERS = 1 << 24
    USE_VAD = 1 << 25
    CHANGE_NICKNAME = 1 << 26
    MANAGE_NICKNAMES = 1 << 27
    MANAGE_ROLES = 1 << 28
    MANAGE_WEBHOOKS = 1 << 29
    MANAGE_EMOJIS_AND_STICKERS = 1 << 30
    USE_APPLICATION_COMMANDS = 1 << 31
    REQUEST_TO_SPEAK = 1 << 32
    MANAGE_EVENTS = 1 << 33
    MANAGE_THREADS = 1 << 34
    CREATE_PUBLIC_THREADS = 1 << 35
    CREATE_PRIVATE_THREADS = 1 << 36
    USE_EXTERNAL_STICKERS = 1 << 37
    SEND_MESSAGES_IN_THREADS = 1 << 38
    START_EMBEDDED_ACTIVITIES = 1 << 39
    MODERATE_MEMBERS = 1 << 40

    DEFAULT = (
        ADD_REACTIONS
        | VIEW_CHANNEL
        | SEND_MESSAGES
        | EMBED_LINKS
        | ATTACH_FILES
        | READ_MESSAGE_HISTORY
        | MENTION_EVERYONE
        | USE_EXTERNAL_EMOJIS
    )
    ALL = (
        DEFAULT
        | CREATE_INSTANT_INVITE
        | KICK_MEMBERS
        | BAN_MEMBERS
        | ADMINISTRATOR
        | MANAGE_CHANNELS
        | MANAGE_GUILD
        | VIEW_AUDIT_LOG
        | PRIORITY_SPEAKER
        | STREAM
        | SEND_TTS_MESSAGES
        | MANAGE_MESSAGES
        | VIEW_GUILD_INSIGHTS
        | CONNECT
        | SPEAK
        | MUTE_MEMBERS
        | DEAFEN_MEMBERS
        | MOVE_MEMBERS
        | USE_VAD
        | CHANGE_NICKNAME
        | MANAGE_NICKNAMES
        | MANAGE_ROLES
        | MANAGE_WEBHOOKS
        | MANAGE_EMOJIS_AND_STICKERS
        | USE_APPLICATION_COMMANDS
        | REQUEST_TO_SPEAK
        | MANAGE_EVENTS
        | MANAGE_THREADS
        | CREATE_PUBLIC_THREADS
        | CREATE_PRIVATE_THREADS
        | USE_EXTERNAL_STICKERS
        | SEND_MESSAGES_IN_THREADS
        | START_EMBEDDED_ACTIVITIES
        | MODERATE_MEMBERS
    )


class UserFlags(IntFlag):
    """An integer flag bitshift object representing the different user flags given by Discord."""

    STAFF = 1
    PARTNER = 1 << 1
    HYPESQUAD = 1 << 2
    BUG_HUNTER_LEVEL_1 = 1 << 3
    HYPESQUAD_HOUSE_1 = 1 << 6
    HYPESQUAD_HOUSE_2 = 1 << 7
    HYPESQUAD_HOUSE_3 = 1 << 8
    PREMIUM_EARLY_SUPPORTER = 1 << 9
    TEAM_PSEUDO_USER = 1 << 10
    SYSTEM = 1 << 12
    BUG_HUNTER_LEVEL_2 = 1 << 14
    VERIFIED_BOT = 1 << 16
    VERIFIED_DEVELOPER = 1 << 17
    DISCORD_CERTIFIED_MODERATOR = 1 << 18
    BOT_HTTP_INTERACTIONS = 1 << 19
    ACTIVE_DEVELOPER = 1 << 22


class AppFlags(IntFlag):
    """An integer flag bitshift object representing the different application flags given by Discord."""

    GATEWAY_PRESENCE = 1 << 12
    GATEWAY_PRESENCE_LIMITED = 1 << 13
    GATEWAY_GUILD_MEMBERS = 1 << 14
    GATEWAY_GUILD_MEMBERS_LIMITED = 1 << 15
    VERIFICATION_PENDING_GUILD_LIMIT = 1 << 16
    EMBEDDED = 1 << 17
    GATEWAY_MESSAGE_CONTENT = 1 << 18
    GATEWAY_MESSAGE_CONTENT_LIMITED = 1 << 19
    APPLICATION_COMMAND_BADGE = 1 << 23


class StatusType(StrEnum):
    """
    An enumerable object representing Discord status icons that a user may have.
    """

    ONLINE = "online"
    DND = "dnd"
    IDLE = "idle"
    INVISIBLE = "invisible"
    OFFLINE = "offline"


class MessageFlags(IntFlag):
    """
    .. versionadded:: 4.4.0

    An integer flag bitshift object representing the different message flags given by Discord.

    :ivar int CROSSPOSTED: this message has been published to subscribed channels (via Channel Following)
    :ivar int IS_CROSSPOST: this message originated from a message in another channel (via Channel Following)
    :ivar int SUPPRESS_EMBEDS: do not include any embeds when serializing this message
    :ivar int SOURCE_MESSAGE_DELETED: the source message for this crosspost has been deleted (via Channel Following)
    :ivar int URGENT: this message came from the urgent message system
    :ivar int HAS_THREAD: this message has an associated thread, with the same id as the message
    :ivar int EPHEMERAL: this message is only visible to the user who invoked the Interaction
    :ivar int LOADING: this message is an Interaction Response and the bot is thinking
    :ivar int FAILED_TO_MENTION_SOME_ROLES_IN_THREAD: this message failed to mention some roles and add their members to the thread
    """

    CROSSPOSTED = 1 << 0
    IS_CROSSPOST = 1 << 1
    SUPPRESS_EMBEDS = 1 << 2
    SOURCE_MESSAGE_DELETED = 1 << 3
    URGENT = 1 << 4
    HAS_THREAD = 1 << 5
    EPHEMERAL = 1 << 6
    LOADING = 1 << 7
    FAILED_TO_MENTION_SOME_ROLES_IN_THREAD = 1 << 8


class MemberFlags(IntFlag):
    """
    .. versionadded:: 4.4.0

    An integer flag bitshift object representing member flags on the guild.

    :ivar int DID_REJOIN: Member has left and rejoined the guild
    :ivar int COMPLETED_ONBOARDING: Member has completed onboarding
    :ivar int BYPASSES_VERIFICATION: Member bypasses guild verification requirements
    :ivar int STARTED_ONBOARDING: Member has started onboarding
    """

    DID_REJOIN = 1 << 0
    COMPLETED_ONBOARDING = 1 << 1
    BYPASSES_VERIFICATION = 1 << 2
    STARTED_ONBOARDING = 1 << 3
