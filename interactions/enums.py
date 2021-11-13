import typing
from enum import IntEnum

from .api.models.channel import Channel
from .api.models.role import Role
from .api.models.user import User


class ApplicationCommandType(IntEnum):
    """
    An enumerable object representing the types of application commands.
    """

    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3
    AUTOCOMPLETE = 4


class InteractionType(IntEnum):
    """
    An enumerable object representing the types of interactions.
    """

    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3


class InteractionCallbackTye(IntEnum):
    """
    An enumerable object representing the callback types of interaction responses.
    """

    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    DEFERRED_UPDATE_MESSAGE = 6
    UPDATE_MESSAGE = 7
    APPLICATION_COMMAND_AUTOCOMPLETE_RESULT = 8


class OptionType(IntEnum):
    """
    Enumerable object of literal integers holding equivocal values of a slash command's option(s).

    .. note::

        Equivalent of `ApplicationCommandOptionType <https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-option-type>`_ in the Discord API.
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
    def from_type(cls, _type: type) -> IntEnum:
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

        if issubclass(_type, Channel):
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

        if issubclass(
            _type, float
        ):  # Python floats are essentially doubles, compared to languages when it's separate.
            return cls.NUMBER


class PermissionType(IntEnum):
    """
    Enumerable object of literal integers holding equivocal values of a slash command's permission(s).

    .. note::
        Equivalent of `ApplicationCommandPermissionType <https://discord.com/developers/docs/interactions/application-commands#application-command-permissions-object-application-command-permission-type>`_ in the Discord API.
    """

    ROLE = 1
    USER = 2

    @classmethod
    def from_type(cls, _type: type) -> IntEnum:
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


class ComponentType(IntEnum):
    """
    Enumerable object of literal integers holding equivocal values of a component(s) type.

    .. note::
        Equivalent of `Component Types <https://discord.com/developers/docs/interactions/message-components#component-object-component-types>`_ in the Discord API.
    """

    ACTION_ROW = 1
    BUTTON = 2
    SELECT = 3


class ButtonType(IntEnum):
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
