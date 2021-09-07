from collections import OrderedDict
from typing import List, Optional, Union

from orjson import dumps

from ..enums import ApplicationCommandType, OptionType, PermissionType


class Choice(object):
    """
    A class object repesenting the choice of an option.

    .. note::
        ``value`` allows ``float`` as a passable value type,
        whereas it's supposed to be ``double``.

    :ivar str name: The name of the choice.
    :ivar typing.Union[str, int, float] value: The returned value of the choice.
    """

    __slots__ = ("name", "value")
    name: str
    value: Union[str, int, float]

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __new__(cls):
        return dumps(cls.__dict__)


class Option(object):
    """
    A class object representing the option of an application command.

    .. note::
        ``options`` is only present for when a subcommand
        has been established.

    :ivar interactions.enums.OptionType type: The type of option.
    :ivar str name: The name of the option.
    :ivar str description: The description of the option.
    :ivar bool required: Whether the option has to be filled out.
    :ivar typing.Optional[typing.List[interactions.models.Choice]] choices: The list of choices to select from.
    :ivar typing.Optional[list] options: The list of subcommand options included.
    """

    __slots__ = ("type", "name", "description", "required", "choices", "options")
    type: OptionType
    name: str
    description: str
    required: bool
    choices: Optional[List[Choice]]
    options: Optional[list]

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __new__(cls):
        comb = OrderedDict()

        for key, value in cls.__dict__:
            if value is not None:
                comb.update({key: value})

        return dumps(comb)


class Permission(object):
    """
    A class object representing the permission of an applicatioon command.

    :ivar int id: The ID of the permission.
    :ivar interactions.enums.PermissionType type: The type of permission.
    :ivar bool permission: The permission state. ``True`` for allow, ``False`` for disallow.
    """

    __slots__ = ("id", "type", "permission")
    id: int
    type: PermissionType
    permission: bool

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __new__(cls):
        return dumps(cls.__dict__)


class ApplicationCommand(object):
    """
    A class object representing all types of commands.

    :ivar typing.Optional[int] id: The ID of the application command.
    :ivar typing.Optional[int] type: The application command type.
    :ivar typing.Optional[int] application_id: The general application ID of the command itself.
    :ivar int guild_id: The guild ID of the application command.
    :ivar str name: The name of the application command.
    :ivar typing.Optional[str] description: The description of the application command.
    :ivar typing.Optional[typing.List[interactions.models.Option]] options: The "options"/arguments of the application command.
    :ivar typing.Optional[bool] default_permission: The default permission accessibility state of the application command.
    """

    __slots__ = (
        "id",
        "type",
        "application_id",
        "guild_id",
        "name",
        "description",
        "options",
        "default_permission",
        "permissions",
    )
    id: Optional[int]
    type: Optional[ApplicationCommandType]
    application_id: Optional[int]
    guild_id: Optional[int]
    name: str
    description: Optional[str]
    options: Optional[List[Option]]
    default_permission: Optional[bool]
    permissions: Optional[List[Permission]]

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __new__(cls):
        comb = OrderedDict()

        for key, value in cls.__dict__:
            if value is not None:
                comb.update({key: value})

        return dumps(comb)
