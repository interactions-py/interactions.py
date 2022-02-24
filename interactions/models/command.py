from typing import Dict, List, Optional, Union

from ..api.models.channel import ChannelType
from ..api.models.misc import DictSerializerMixin, Snowflake
from ..enums import ApplicationCommandType, OptionType, PermissionType


class Choice(DictSerializerMixin):
    """
    A class object representing the choice of an option.

    .. note::
        ``value`` allows ``float`` as a passable value type,
        whereas it's supposed to be ``double``.

    The structure for a choice:

    .. code-block:: python

        interactions.Choice(name="Choose me! :(", value="choice_one")

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

    The structure for an option:

    .. code-block:: python

        interactions.Option(
            type=interactions.OptionType.STRING,
            name="option_name",
            description="i'm a meaningless option in your life. (depressed noises)",
            required=True,
            choices=[interactions.Choice(...)], # optional
        )

    :ivar OptionType type: The type of option.
    :ivar str name: The name of the option.
    :ivar str description: The description of the option.
    :ivar bool focused: Whether the option is currently being autocompleted or not.
    :ivar Optional[bool] required?: Whether the option has to be filled out.
    :ivar Optional[str] value?: The value that's currently typed out, if autocompleting.
    :ivar Optional[List[Choice]] choices?: The list of choices to select from.
    :ivar Optional[List[Option]] options?: The list of subcommand options included.
    :ivar Optional[List[ChannelType]] channel_types?: Restrictive shown channel types, if given.
    :ivar Optional[int] min_value?: The minimum value supported by the option.
    :ivar Optional[int] max_value?: The maximum value supported by the option.
    :ivar Optional[bool] autocomplete?: A status denoting whether this option is an autocomplete option.
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
        "name_localizations",
        "description_localizations",
    )
    _json: dict
    type: OptionType
    name: str
    description: str
    focused: bool
    required: Optional[bool]
    value: Optional[str]
    choices: Optional[List[Choice]]
    options: Optional[List["Option"]]
    channel_types: Optional[List[ChannelType]]
    min_value: Optional[int]
    max_value: Optional[int]
    autocomplete: Optional[bool]

    name_localizations: Optional[Dict[str, str]]  # TODO: post-v4: document these when Discord does.
    description_localizations: Optional[Dict[str, str]]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.type = OptionType(self.type)
        self._json.update({"type": self.type.value})
        if self._json.get("options"):
            if all(isinstance(option, dict) for option in self.options):
                self._json["options"] = list(self.options)
            else:
                self._json["options"] = [
                    option if isinstance(option, dict) else option._json for option in self.options
                ]
        if self.choices:
            if all(isinstance(choice, dict) for choice in self.choices):
                if isinstance(self._json.get("choices"), dict):
                    self._json["choices"] = list(self.choices)
                else:
                    self._json["choices"] = [
                        choice if isinstance(choice, dict) else choice._json
                        for choice in self.choices
                    ]
            elif all(isinstance(choice, Choice) for choice in self.choices):
                self._json["choices"] = [choice._json for choice in self.choices]


class Permission(DictSerializerMixin):
    """
    A class object representing the permission of an application command.

    The structure for a permission:

    .. code-block:: python

        interactions.Permission(
            id=1234567890,
            type=interactions.PermissionType.USER,
            permission=True,
        )

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
        self.type = PermissionType(self.type)
        self._json.update({"type": self.type.value})


class ApplicationCommand(DictSerializerMixin):
    """
    A class object representing all types of commands.

    .. warning::
        This object is inferred upon whenever the client is caching
        information about commands from an HTTP request and/or the
        Gateway. Do not use this object for declaring commands.

    :ivar Snowflake id: The ID of the application command.
    :ivar ApplicationCommandType type: The application command type.
    :ivar Optional[Snowflake] application_id?: The general application ID of the command itself.
    :ivar Optional[Snowflake] guild_id?: The guild ID of the application command.
    :ivar str name: The name of the application command.
    :ivar str description: The description of the application command.
    :ivar Optional[List[Option]] options?: The "options"/arguments of the application command.
    :ivar Optional[bool] default_permission?: The default permission accessibility state of the application command.
    :ivar int version: The Application Command version autoincrement identifier.
    :ivar str default_member_permissions: The default member permission state of the application command.
    :ivar boolean dm_permission: The application permissions if executed in a Direct Message.
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
        "description_localizations",
        "name_localizations",
    )
    _json: dict
    id: Snowflake
    type: ApplicationCommandType
    application_id: Optional[Snowflake]
    guild_id: Optional[Snowflake]
    name: str
    description: str
    options: Optional[List[Option]]
    default_permission: Optional[bool]
    permissions: Optional[List[Permission]]
    version: int

    # TODO: post-v4: Investigate these once documented by Discord.
    default_member_permissions: str
    dm_permission: bool

    # TODO: post-v4: Document once Discord does.
    name_localizations: Optional[Dict[str, str]]
    description_localizations: Optional[Dict[str, str]]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.application_id = (
            Snowflake(self.application_id) if self._json.get("application_id") else None
        )
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.options = (
            [Option(**option) for option in self.options] if self._json.get("options") else None
        )
        self.permissions = (
            [Permission(**permission) for permission in self.permissions]
            if self._json.get("permissions")
            else None
        )
