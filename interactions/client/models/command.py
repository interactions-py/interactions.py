from typing import Dict, List, Optional, Union

from ...api.models.attrs_utils import DictSerializerMixin, convert_list, define, field
from ...api.models.channel import ChannelType
from ...api.models.misc import Snowflake
from ..enums import ApplicationCommandType, Locale, OptionType, PermissionType

__all__ = (
    "Choice",
    "Option",
    "Permission",
    "ApplicationCommand",
)


@define()
class Choice(DictSerializerMixin):
    """
    A class object representing the choice of an option.

    .. note::
        ``value`` allows ``float`` as a passable value type,
        whereas it's supposed to be ``double``.

    The structure for a choice: ::

        interactions.Choice(name="Choose me! :(", value="choice_one")

    :ivar str name: The name of the choice.
    :ivar Union[str, int, float] value: The returned value of the choice.
    :ivar Optional[Dict[Union[str, Locale], str]] name_localizations?: The dictionary of localization for the ``name`` field. This enforces the same restrictions as the ``name`` field.
    """

    _json: dict = field()
    name: str = field()
    value: Union[str, int, float] = field()
    name_localizations: Optional[Dict[Union[str, Locale], str]] = field()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        if self._json.get("name_localizations"):
            if any(
                type(x) != str for x in self._json.get("name_localizations")
            ):  # check if Locale object is used to create localisation at any certain point.
                self._json["name_localizations"] = {
                    k.value if isinstance(k, Locale) else k: v
                    for k, v in self._json["name_localizations"].items()
                }
            self.name_localizations = {
                k if isinstance(k, Locale) else Locale(k): v
                for k, v in self._json["name_localizations"].items()
            }


@define()
class Option(DictSerializerMixin):
    """
    A class object representing the option of an application command.

    .. note::
        ``options`` is only present for when a subcommand
        has been established.

        ``min_values`` and ``max_values`` are useful primarily for
        integer based options.

    The structure for an option: ::

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
    :ivar Optional[Dict[Union[str, Locale], str]] name_localizations?: The dictionary of localization for the ``name`` field. This enforces the same restrictions as the ``name`` field.
    :ivar Optional[Dict[Union[str, Locale], str]] description_localizations?: The dictionary of localization for the ``description`` field. This enforces the same restrictions as the ``description`` field.
    """

    type: OptionType = field(converter=OptionType)
    name: str = field()
    description: str = field(default=None)
    focused: bool = field(default=False)
    required: Optional[bool] = field(default=None)
    value: Optional[str] = field(default=None)
    choices: Optional[List[Choice]] = field(converter=convert_list(Choice), default=None)
    options: Optional[List["Option"]] = field(default=None)
    channel_types: Optional[List[ChannelType]] = field(
        converter=convert_list(ChannelType), default=None
    )
    min_value: Optional[int] = field(default=None)
    max_value: Optional[int] = field(default=None)
    autocomplete: Optional[bool] = field(default=None)
    name_localizations: Optional[Dict[Union[str, Locale], str]] = field(
        default=None
    )  # this may backfire
    description_localizations: Optional[Dict[Union[str, Locale], str]] = field(
        default=None
    )  # so can this

    def __attrs_post_init__(self):
        # needed for nested classes
        self.options = (
            [Option(**option) if isinstance(option, dict) else option for option in self.options]
            if self.options is not None
            else None
        )


@define()
class Permission(DictSerializerMixin):
    """
    A class object representing the permission of an application command.

    The structure for a permission: ::

        interactions.Permission(
            id=1234567890,
            type=interactions.PermissionType.USER,
            permission=True,
        )
    :ivar int id: The ID of the permission.
    :ivar PermissionType type: The type of permission.
    :ivar bool permission: The permission state. ``True`` for allow, ``False`` for disallow.
    """

    id: int = field()
    type: PermissionType = field(converter=PermissionType)
    permission: bool = field()

    def __attrs_post_init__(self):
        self._json["type"] = self.type.value


@define()
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
    :ivar Optional[Dict[Union[str, Locale], str]] name_localizations: The localisation dictionary for the application command name, if any.
    :ivar Optional[Dict[Union[str, Locale], str]] description_localizations: The localisation dictionary for the application command description, if any.
    """

    id: Snowflake = field(converter=Snowflake, default=None)
    type: ApplicationCommandType = field(converter=ApplicationCommandType)
    application_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    guild_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    name: str = field()
    description: str = field()
    options: Optional[List[Option]] = field(converter=convert_list(Option), default=None)
    default_permission: Optional[bool] = field(default=None)
    version: int = field(default=None)
    default_member_permissions: str = field()
    dm_permission: bool = field()
    name_localizations: Optional[Dict[Union[str, Locale], str]] = field(default=None)
    description_localizations: Optional[Dict[Union[str, Locale], str]] = field(default=None)
