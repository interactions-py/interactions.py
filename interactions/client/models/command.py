from inspect import getdoc
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, List, Optional, Union

from ...api.models.attrs_utils import MISSING, DictSerializerMixin, convert_list, define, field
from ...api.models.channel import Channel, ChannelType
from ...api.models.member import Member
from ...api.models.message import Attachment
from ...api.models.misc import File, Image, Snowflake
from ...api.models.role import Role
from ...api.models.user import User
from ..enums import ApplicationCommandType, Locale, OptionType, PermissionType

if TYPE_CHECKING:
    from ..context import CommandContext

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

    name: str = field()
    value: Union[str, int, float] = field()
    name_localizations: Optional[Dict[Union[str, Locale], str]] = field(default=None)

    def __attrs_post_init__(self):
        if self._json.get("name_localizations"):
            if any(
                type(x) != str for x in self._json["name_localizations"]
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
    dm_permission: bool = field(default=None)
    name_localizations: Optional[Dict[Union[str, Locale], str]] = field(default=None)
    description_localizations: Optional[Dict[Union[str, Locale], str]] = field(default=None)


def option(
    _type: OptionType,
    /,
    name: str,
    description: Optional[str] = "No description",
    choices: Optional[List[Choice]] = None,
    required: Optional[bool] = True,
    channel_types: Optional[List[ChannelType]] = None,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
    options: Optional[List[Option]] = None,
    autocomplete: Optional[bool] = None,
    focused: Optional[bool] = None,
    value: Optional[str] = None,
    name_localizations: Optional[Dict[Union[str, Locale], str]] = None,
    description_localizations: Optional[Dict[Union[str, Locale], str]] = None,
):
    """
    docstring
    """  # TODO: change docstring

    def decorator(coro: Callable[..., Awaitable]):
        if isinstance(_type, int):
            type_ = _type
        elif _type in (str, int, float, bool):
            if _type is str:
                type_ = OptionType.STRING
            elif _type is int:
                type_ = OptionType.INTEGER
            elif _type is float:
                type_ = OptionType.NUMBER
            elif _type is bool:
                type_ = OptionType.BOOLEAN
        elif isinstance(_type, OptionType):
            type_ = _type
        elif _type in (Member, User):
            type_ = OptionType.USER
        elif _type is Channel:
            type_ = OptionType.CHANNEL
        elif _type is Role:
            type_ = OptionType.ROLE
        elif _type in (Attachment, File, Image):
            type_ = OptionType.ATTACHMENT
        else:
            raise TypeError(f"Invalid type: {_type}")  # TODO: change error

        option: Option = Option(
            type=type_,
            name=name,
            description=description,
            choices=choices,
            required=required,
            channel_types=channel_types,
            min_value=min_value,
            max_value=max_value,
            options=options,
            autocomplete=autocomplete,
            focused=focused,
            value=value,
            name_localizations=name_localizations,
            description_localizations=description_localizations,
        )
        if hasattr(coro, "_options"):
            coro._options.insert(0, option)
        else:
            coro._options = [option]

        return coro

    return decorator


class StopCommand:
    """
    A class that when returned from a command, the command chain is stopped.

    Usage:
    ```py
    @bot.command()
    async def foo(ctx):
        ... # do something
        return StopCommand  # does not execute `bar`
        # or `return StopCommand()`

    @foo.subcommand()
    async def bar(ctx): ...
    ```
    """  # TODO: change docstring


@define()
class BaseResult(DictSerializerMixin):
    """docstring"""  # TODO: change docstring

    result: Any = field()

    def __call__(self) -> Any:
        return self.result


@define()
class GroupResult(DictSerializerMixin):
    """docstring"""  # TODO: change docstring

    result: Any = field()
    parent: BaseResult = field()

    def __call__(self) -> Any:
        return self.result


@define()
class Command(DictSerializerMixin):
    """docstring"""  # TODO: change docstring

    client: "Client" = field()  # noqa
    coro: Callable[..., Awaitable] = field()
    type: ApplicationCommandType = field(converter=ApplicationCommandType)
    base: str = field()
    description: str = field()
    options: Optional[List[Option]] = field(converter=convert_list(Option), default=None)
    scope: List[int] = field(converter=convert_list(int))
    version: int = field(default=None)
    default_member_permissions: str = field()
    dm_permission: bool = field(default=None)
    name_localizations: Optional[Dict[Union[str, Locale], str]] = field(default=None)
    description_localizations: Optional[Dict[Union[str, Locale], str]] = field(default=None)

    def __attrs_post_init__(self) -> None:
        self.coroutines: Dict[str, Callable[..., Awaitable]] = {}
        if self.base in (MISSING, None):
            self.base = self.coro.__name__
        if self.description in (MISSING, None) and self.type == ApplicationCommandType.CHAT_INPUT:
            self.description = getdoc(self.coro) or "No description set"
            self.description = self.description.split("\n", 1)[0]
        if hasattr(self.coro, "_options"):
            if not self.options:
                self.options = self.coro._options
            else:
                self.options.extend(self.coro._options)

    def __call__(self, *args, **kwargs) -> Awaitable:
        return self.coro(*args, **kwargs)

    @property
    def full_data(self) -> List[dict]:
        """Returns the command in JSON format."""  # TODO: change docstring
        from ..decor import command

        data = command(
            type=self.type,
            name=self.base,
            description=self.description if self.type == 1 else None,
            options=self.options,
            scope=self.scope,
            name_localizations=self.name_localizations,
            description_localizations=self.description_localizations,
            default_member_permissions=self.default_member_permissions,
            dm_permission=self.dm_permission,
        )
        return data if isinstance(data, list) else [data]

    def check_options(self) -> None:
        if self.type != ApplicationCommandType.CHAT_INPUT:
            raise ValueError("Only chat input commands can have subcommands.")  # TODO: change error
        if any(
            option.type not in (OptionType.SUB_COMMAND, OptionType.SUB_COMMAND_GROUP)
            for option in self.options
        ):
            raise ValueError(
                "Subcommands are incompatible with base command options."
            )  # TODO: change error

    def subcommand(
        self,
        *,
        group: Optional[str] = MISSING,
        name: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        options: Optional[List[Option]] = MISSING,
        name_localizations: Optional[Dict[Union[str, Locale], str]] = MISSING,
        description_localizations: Optional[Dict[Union[str, Locale], str]] = MISSING,
    ) -> Callable[[Callable], "Command"]:
        """
        Creates a subcommand of the command.
        """  # TODO: change docstring

        self.check_options()

        def decorator(coro: Callable[..., Awaitable]) -> "Command":
            _name = coro.__name__ if name is MISSING else name
            _description = description
            if description in (MISSING, None):
                _description = getdoc(coro) or "No description set"
                _description = _description.split("\n", 1)[0]
            _options = options
            if hasattr(coro, "_options"):
                if options in (MISSING, None):
                    _options = coro._options
                else:
                    _options.extend(coro._options)
            if name_localizations is MISSING:
                _name_localizations = self.name_localizations
            else:
                _name_localizations = name_localizations
            if description_localizations is MISSING:
                _description_localizations = self.description_localizations
            else:
                _description_localizations = description_localizations
            self.coroutines[_name] = coro

            subcommand = Option(
                type=OptionType.SUB_COMMAND,
                name=_name,
                description=_description,
                options=_options,
                name_localizations=_name_localizations,
                description_localizations=_description_localizations,
            )

            if group is MISSING:
                self.options.append(subcommand)
            else:
                for i, option in enumerate(self.options):
                    if option.name == group:
                        break
                else:
                    self.group(name=group)(coro)
                    for i, option in enumerate(self.options):
                        if option.name == group:
                            break
                self.options[i].options.append(subcommand)
                self.options[i]._json["options"].append(subcommand._json)

            return self

        return decorator

    def group(
        self,
        *,
        name: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        options: Optional[List[Option]] = MISSING,
        name_localizations: Optional[Dict[Union[str, Locale], str]] = MISSING,
        description_localizations: Optional[Dict[Union[str, Locale], str]] = MISSING,
    ) -> Callable[[Callable], "Command"]:
        """Creates a group option"""  # TODO: change docstring

        self.check_options()

        def decorator(coro: Callable[..., Awaitable]) -> "Command":
            _name = coro.__name__ if name is MISSING else name
            _description = description
            if description in (MISSING, None):
                _description = getdoc(coro) or "No description set"
                _description = _description.split("\n", 1)[0]
            _options = options
            if hasattr(coro, "_options"):
                if options in (MISSING, None):
                    _options = coro._options
                else:
                    _options.extend(coro._options)
            if name_localizations is MISSING:
                _name_localizations = self.name_localizations
            else:
                _name_localizations = name_localizations
            if description_localizations is MISSING:
                _description_localizations = self.description_localizations
            else:
                _description_localizations = description_localizations
            self.coroutines[_name] = coro

            group = Option(
                type=OptionType.SUB_COMMAND_GROUP,
                name=_name,
                description=_description,
                options=_options,
                name_localizations=_name_localizations,
                description_localizations=_description_localizations,
            )
            self.options.append(group)

            return self

        return decorator

    async def dispatcher(
        self,
        ctx: "CommandContext",
        *args,
        sub_command_group: Optional[str] = None,
        sub_command: Optional[str] = None,
        **kwargs,
    ) -> Optional[Any]:
        """Calls all of the coroutines of the subcommand."""  # TODO: change docstring
        base_coro = self.base_coroutine
        if self._self:
            base_res = BaseResult(result=await base_coro(self._self, ctx, *args, **kwargs))
            if base_res() is StopCommand or isinstance(base_res(), StopCommand):
                return
            if self.data:
                if sub_command_group:
                    group_coro = self.coroutines[sub_command_group]
                    subcommand_coro = self.coroutines[f"{sub_command_group} {sub_command}"]
                    group_res = GroupResult(
                        result=await group_coro(self._self, ctx, base_res, *args, **kwargs),
                        parent=base_res,
                    )
                    if group_res() is StopCommand or isinstance(group_res(), StopCommand):
                        return
                    return await subcommand_coro(self._self, ctx, group_res, *args, **kwargs)
                elif sub_command:
                    subcommand_coro = self.coroutines[sub_command]
                    return await subcommand_coro(self._self, ctx, base_res, *args, **kwargs)
            return base_res
        base_res = BaseResult(result=await base_coro(ctx, *args, **kwargs))
        if base_res() is StopCommand or isinstance(base_res(), StopCommand):
            return
        if self.data:
            if sub_command_group:
                group_coro = self.coroutines[sub_command_group]
                subcommand_coro = self.coroutines[f"{sub_command_group} {sub_command}"]
                group_res = GroupResult(
                    result=await group_coro(ctx, base_res, *args, **kwargs), parent=base_res
                )
                if group_res() is StopCommand or isinstance(group_res(), StopCommand):
                    return
                return await subcommand_coro(ctx, group_res, *args, **kwargs)
            elif sub_command:
                subcommand_coro = self.coroutines[sub_command]
                return await subcommand_coro(ctx, base_res, *args, **kwargs)
        return base_res
