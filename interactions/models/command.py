from typing import Any, List, Optional, Union

from ..api.models.channel import ChannelType
from ..api.models.misc import DictSerializerMixin
from ..enums import ApplicationCommandType, OptionType, PermissionType


class Choice(DictSerializerMixin):
    """
    A class object representing the choice of an option.

    .. note::
        ``value`` allows ``float`` as a passable value type,
        whereas it's supposed to be ``double``.

    :ivar str name: The name of the choice.
    :ivar Union[str, int, float] value: The returned value of the choice.
    """

    __slots__ = ("_json", "name", "value")
    _json: dict
    name: str
    value: Union[str, int, float]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


class Option(DictSerializerMixin):
    """
    A class object representing the option of an application command.

    .. note::
        ``options`` is only present for when a subcommand
        has been established.

        ``min_values`` and ``max_values`` are useful primarily for
        integer based options.

    :ivar OptionType type: The type of option.
    :ivar str name: The name of the option.
    :ivar str description: The description of the option.
    :ivar bool focused: Whether the option is currently being autocompleted or not.
    :ivar bool required?: Whether the option has to be filled out.
    :ivar Optional[str] value?: The value that's currently typed out, if autocompleting.
    :ivar Optional[List[Choice]] choices?: The list of choices to select from.
    :ivar Optional[List[Option]] options?: The list of subcommand options included.
    :ivar Optional[List[ChannelType] channel_types?: Restrictive shown channel types, if given.
    :ivar Optional[int] min_value: The minimum value supported by the option.
    :ivar Optional[int] max_value: The maximum value supported by the option.
    :ivar Optional[bool] autocomplete: A status denoting whether this option is an autocomplete option.
    """

    __slots__ = (
        "_json",
        "type",
        "name",
        "description",
        "focused",
        "required",
        "value",
        "choices",
        "options",
        "channel_types",
        "min_value",
        "max_value",
        "autocomplete",
    )
    _json: dict
    type: OptionType
    name: str
    description: str
    focused: bool
    required: Optional[bool]
    value: Optional[str]
    choices: Optional[List[Choice]]
    options: Optional[list]
    channel_types: Optional[List[ChannelType]]
    min_value: Optional[OptionType]
    max_value: Optional[OptionType]
    autocomplete: Optional[bool]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._json["type"] = OptionType(kwargs["type"]).value
        if self._json.get("choices"):
            self._json["choices"] = [choice._json for choice in self.choices]


class Permission(DictSerializerMixin):
    """
    A class object representing the permission of an application command.

    :ivar int id: The ID of the permission.
    :ivar PermissionType type: The type of permission.
    :ivar bool permission: The permission state. ``True`` for allow, ``False`` for disallow.
    """

    __slots__ = ("_json", "id", "type", "permission")
    _json: dict
    id: int
    type: PermissionType
    permission: bool

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._json["type"] = PermissionType(kwargs["type"]).value


class ApplicationCommand(DictSerializerMixin):
    """
    A class object representing all types of commands.

    :ivar int id: The ID of the application command.
    :ivar ApplicationCommandType type: The application command type.
    :ivar Optional[int] application_id?: The general application ID of the command itself.
    :ivar Optional[int] guild_id?: The guild ID of the application command.
    :ivar str name: The name of the application command.
    :ivar str description: The description of the application command.
    :ivar Optional[List[Option]] options?: The "options"/arguments of the application command.
    :ivar Optional[bool] default_permission?: The default permission accessibility state of the application command.
    :ivar int version: The Application Command version autoincrement identifier.
    :ivar typing.Any default_member_permissions: The default member permission state of the application command.
    :ivar typing.Any dm_permission: The application permissions if executed in a Direct Message.
    """

    __slots__ = (
        "_json",
        "id",
        "type",
        "application_id",
        "guild_id",
        "name",
        "description",
        "options",
        "default_permission",
        "permissions",
        "version",
        "default_member_permissions",
        "dm_permission",
    )
    _json: dict
    id: int
    type: ApplicationCommandType
    application_id: Optional[int]
    guild_id: Optional[int]
    name: str
    description: str
    options: Optional[List[Option]]
    default_permission: Optional[bool]
    permissions: Optional[List[Permission]]
    version: int

    # TODO: Investigate these. These are apparently a thing.
    # TODO: And document them.
    default_member_permissions: Optional[Any]
    dm_permission: Optional[Any]  # Could be any idk

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
