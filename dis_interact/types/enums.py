import typing
from enum import IntEnum

from discord import Member
from discord.abc import Messageable, User, Role, GuildChannel


class DefaultErrorEnum(IntEnum):
    """
    This is a port from v3's errors, which basically delegate errors to a unique error code.

    ..note::
        This enum's purpose is to help remember error codes. Importing this class is not required.
        i.e.:
            raise InteractionException(1) == raise InteractionException(REQUEST_FAILURE)
    """

    BASE = 0
    REQUEST_FAILURE = 1
    INCORRECT_FORMAT = 2
    DUPLICATE_COMMAND = 3
    DUPLICATE_CALLBACK = 4
    DUPLICATE_SLASH_CLIENT = 5
    CHECK_FAILURE = 6
    INCORRECT_TYPE = 7
    INCORRECT_GUILD_ID_TYPE = 8
    INCORRECT_COMMAND_DATA = 9
    ALREADY_RESPONDED = 10


class WebSocketOPCodes(IntEnum):
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    PRESENCE = 3
    VOICE_STATE = 4
    VOICE_PING = 5
    RESUME = 6
    RECONNECT = 7
    REQUEST_MEMBERS = 8
    INVALIDATE_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11
    GUILD_SYNC = 12


class WebSocketCloseCodes(IntEnum):
    UNKNOWN_ERROR = 4000
    UNKNOWN_OPCODE = 4001
    DECODE_ERROR = 4002
    NOT_AUTHENTICATED = 4003
    AUTHENTICATION_FAILED = 4004
    ALREADY_AUTHENTICATED = 4005
    INVALID_SEQ = 4007
    RATE_LIMITED = 4008
    SESSION_TIMED_OUT = 4009
    INVALID_SHARD = 4010
    SHARDING_REQUIRED = 4011
    INVALID_API_VERSION = 4012
    INVALID_INTENTS = 4013
    DISALLOWED_INTENTS = 4014


class HTTPResponse(IntEnum):
    """
    Lists all of the HTTP response codes Discord gives out.

    ..note::
        This enum does not list the documented "5xx", as it may vary.
    """

    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    NOT_MODIFIED = 304
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    TOO_MANY_REQUESTS = 429
    GATEWAY_UNAVAILABLE = 502


class Channel(IntEnum):
    """
    Types of channels.

    ..note::
        While all of them are listed, not all of them would be used at this lib's scope.
    """

    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6
    GUILD_NEWS_THREAD = 10
    GUILD_PUBLIC_THREAD = 11
    GUILD_PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13


class Message(IntEnum):
    """Type of messages.

    ..note::
        While all of them are listed, not all of them would be used at this lib's scope.
    """

    DEFAULT = 0
    RECIPIENT_ADD = 1
    RECIPIENT_REMOVE = 2
    CALL = 3
    CHANNEL_NAME_CHANGE = 4
    CHANNEL_ICON_CHANGE = 5
    CHANNEL_PINNED_MESSAGE = 6
    GUILD_MEMBER_JOIN = 7
    USER_PREMIUM_GUILD_SUBSCRIPTION = 8
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_1 = 9
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2 = 10
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3 = 11
    CHANNEL_FOLLOW_ADD = 12
    GUILD_DISCOVERY_DISQUALIFIED = 14
    GUILD_DISCOVERY_REQUALIFIED = 15
    GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING = 16
    GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING = 17
    THREAD_CREATED = 18
    REPLY = 19
    APPLICATION_COMMAND = 20
    THREAD_STARTER_MESSAGE = 21
    GUILD_INVITE_REMINDER = 22


class Intents(IntEnum):
    """
    Intent flags defined by the Discord API.
    """

    # Base intents, exactly from the API
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

    # Shortcuts/grouping/aliases
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
    )

    MESSAGES = GUILD_MESSAGES | DIRECT_MESSAGES
    REACTIONS = GUILD_MESSAGE_REACTIONS | DIRECT_MESSAGE_REACTIONS
    TYPING = GUILD_MESSAGE_TYPING | DIRECT_MESSAGE_TYPING

    PRIVILEGED = GUILD_PRESENCES | GUILD_MEMBERS

    NONE = 0  # No intents
    ALL = DEFAULT | PRIVILEGED  # All intents are the regular + "requested" intents.

    @classmethod
    def all(cls) -> int:
        """Returns all of the intents."""
        return cls.ALL

    @classmethod
    def default(cls) -> int:
        """Returns the default intents."""
        return cls.DEFAULT


class Options(IntEnum):
    """
    Enumerable object of literal integers holding equivocal values of a slash command's option(s).

    .. note::

        Equivalent of `ApplicationCommandOptionType <https://discord.com/developers/docs/interactions/slash-commands#applicationcommandoptiontype>`_ in the Discord API.
    """
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
    MENTIONABLE = 9
    NUMBER = 10

    @classmethod
    def from_type(
            cls,
            _type: type
    ) -> IntEnum:
        """
        Get a specific enumerable from a type or object.

        :param _type: The type or object to get an enumerable integer for.
        :type _type: type
        :return: enum.IntEnum.
        """
        if issubclass(_type, str):
            return cls.STRING

        if issubclass(_type, int):
            return cls.INTEGER

        if issubclass(_type, bool):
            return cls.BOOLEAN

        if issubclass(_type, User):
            return cls.USER

        if issubclass(_type, GuildChannel):
            return cls.CHANNEL

        if issubclass(_type, Role):
            return cls.ROLE

        if hasattr(typing, "_GenericAlias"):  # 3.7 onwards
            # Easier than imports
            if hasattr(_type, "__origin__"):
                if _type.__origin__ is typing.Union:
                    # proven in 3.7.8+, 3.8.6+, 3.9+ definitively
                    return cls.MENTIONABLE
        if not hasattr(typing, "_GenericAlias"):  # py 3.6
            if isinstance(_type, typing._Union):  # noqa
                return cls.MENTIONABLE

        if issubclass(_type, float):  # Python floats are essentially doubles, compared to languages when it's separate.
            return cls.NUMBER


class Permissions(IntEnum):
    """
    Enumerable object of literal integers holding equivocal values of a slash command's permission(s).

    .. note::

        Equivalent of `ApplicationCommandPermissionType <https://discord.com/developers/docs/interactions/slash-commands#applicationcommandpermissiontype>`_ in the Discord API.
    """
    ROLE = 1
    USER = 2

    @classmethod
    def from_type(
            cls,
            _type: type
    ) -> IntEnum:
        """
        Get a specific enumerable from a type or object.

        :param _type: The type or object to get an enumerable integer for.
        :type _type: type
        :return: enum.IntEnum.
        """
        if issubclass(_type, Role):
            return cls.ROLE

        if issubclass(_type, User):
            return cls.USER


class Components(IntEnum):
    """
    Enumerable object of literal integers holding equivocal values of a component(s) type.

    .. note::

        Equivalent of `Component Types <https://discord.com/developers/docs/interactions/message-components#component-object-component-types>`_ in the Discord API.
    """
    ACTION_ROW = 1
    BUTTON = 2
    SELECT = 3


class Buttons(IntEnum):
    """
    Enumerable object of literal integers holding equivocal values of a button(s) type.

    .. note::

        Equivalent of `Button Styles <https://discord.com/developers/docs/interactions/message-components#button-object-button-styles>`_ in the Discord API.
    """
    BLUE = 1
    BLURPLE = 2
    GRAY = 2
    GREY = 2
    GREEN = 3
    RED = 4

    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    URL = 5


class Menus(IntEnum):
    """
    Enumerable object of literal integers holding equivocal values of a menu type for commands.

    .. note::

        Equivalent of `Application Command Types <https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-types>`_ in the Discord API.
    """
    CHAT_INPUT = 1
    COMMAND = 1  # alias of CHAT_INPUT
    USER = 2
    MESSAGE = 3

    @classmethod
    def from_type(
            cls,
            _type: type
    ) -> IntEnum:
        """
        Get a specific enumerable from a type or object.

        :param _type: The type or object to get an enumerable integer for.
        :type _type: type
        :return: enum.IntEnum.
        """
        if (
                isinstance(_type, Member) or
                issubclass(_type, User)
        ):
            return cls.USER

        if issubclass(_type, Messageable):
            return cls.MESSAGE
