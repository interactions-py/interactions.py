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
    FLOAT = 10

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
            if isinstance(t, typing._Union):  # noqa
                return cls.MENTIONABLE

        if issubclass(_type, float):
            return cls.FLOAT


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
