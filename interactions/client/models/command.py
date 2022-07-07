from functools import wraps
from inspect import getdoc
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Coroutine, Dict, List, Optional, Union

from ...api.error import LibraryException
from ...api.models.attrs_utils import MISSING, DictSerializerMixin, convert_list, define, field
from ...api.models.channel import Channel, ChannelType
from ...api.models.guild import Guild
from ...api.models.member import Member
from ...api.models.message import Attachment
from ...api.models.misc import File, Image, Snowflake
from ...api.models.role import Role
from ...api.models.user import User
from ..enums import ApplicationCommandType, Locale, OptionType, PermissionType

if TYPE_CHECKING:
    from ..bot import Extension
    from ..context import CommandContext

__all__ = (
    "Choice",
    "Option",
    "Permission",
    "ApplicationCommand",
    "option",
    "StopCommand",
    "Command",
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
    description: Optional[str] = "No description set",
    choices: Optional[List[Choice]] = None,
    required: Optional[bool] = None,
    channel_types: Optional[List[ChannelType]] = None,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
    options: Optional[List[Option]] = None,
    autocomplete: Optional[bool] = None,
    focused: Optional[bool] = None,
    value: Optional[str] = None,
    name_localizations: Optional[Dict[Union[str, Locale], str]] = None,
    description_localizations: Optional[Dict[Union[str, Locale], str]] = None,
) -> Callable[..., Callable[..., Awaitable]]:
    """
    A decorator for adding options to a command.

    The structure of an option: ::

        @client.command()
        @interactions.option(str, name="opt", ...)
        async def my_command(ctx, opt: str):
            ...

    :param _type: The type of the option.
    :type _type: OptionType
    :param name: The name of the option.
    :type name: str
    :param description?: The description of the option. Defaults to ``"No description set"``.
    :type description: str
    :param choices?: The choices of the option.
    :type choices: Optional[List[Choice]]
    :param required?: Whether the option has to be filled out.
    :type required: Optional[bool]
    :param channel_types?: Restrictive shown channel types, if given.
    :type channel_types: Optional[List[ChannelType]]
    :param min_value?: The minimum value supported by the option.
    :type min_value: Optional[int]
    :param max_value?: The maximum value supported by the option.
    :type max_value: Optional[int]
    :param options?: The list of subcommand options included.
    :type options: Optional[List[Option]]
    :param autocomplete?: A status denoting whether this option is an autocomplete option.
    :type autocomplete: Optional[bool]
    :param focused?: Whether the option is currently being autocompleted or not.
    :type focused: Optional[bool]
    :param value?: The value that's currently typed out, if autocompleting.
    :type value: Optional[str]
    :param name_localizations?: The dictionary of localization for the ``name`` field. This enforces the same restrictions as the ``name`` field.
    :type name_localizations: Optional[Dict[Union[str, Locale], str]]
    :param description_localizations?: The dictionary of localization for the ``description`` field. This enforces the same restrictions as the ``description`` field.
    :type description_localizations: Optional[Dict[Union[str, Locale], str]]
    """

    def decorator(coro: Callable[..., Awaitable]) -> Callable[..., Awaitable]:
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
            raise LibraryException(code=7, message=f"Invalid type: {_type}")

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

        if hasattr(coro, "_options") and isinstance(coro._options, list):
            coro._options.insert(0, option)
        else:
            coro._options = [option]

        return coro

    return decorator


class StopCommand:
    """
    A class that when returned from a command, the command chain is stopped.

    Usage: ::

        @bot.command()
        async def foo(ctx):
            ... # do something
            return StopCommand  # does not execute `bar`
            # or `return StopCommand()`

        @foo.subcommand()
        async def bar(ctx):
            ...  # `bar` is not executed
    """


@define()
class BaseResult(DictSerializerMixin):
    """
    A class object representing the result of the base command.

    Usage: ::

        @bot.command()
        async def foo(ctx):
            ... # do something
            return "done"  # return something

        @foo.subcommand()
        async def bar(ctx, base_res: BaseResult):
            print(base_res.result)  # "done"

    .. note::
        If the subcommand does not have enough arguments, the ``BaseResult`` will not be passed.

    :ivar Any result: The result of the base command.
    """

    result: Any = field(repr=True)

    def __call__(self) -> Any:
        return self.result


@define()
class GroupResult(DictSerializerMixin):
    """
    A class object representing the result of the base command.

    Usage: ::

        @bot.command()
        async def foo(ctx):
            ... # do something
            return "done base"  # return something

        @foo.group()
        async def bar(ctx, base_res: BaseResult):
            print(base_res.result)  # "done base"
            return "done group"  # return something

        @bar.subcommand()
        async def pseudo(ctx, group_res: GroupResult):
            print(group_res.result)  # "done group"
            print(group_res.parent)  # BaseResult(result='done base')

    .. note::
        If the subcommand does not have enough arguments, the ``GroupResult`` will not be passed.

    :ivar Any result: The result of the base command.
    :ivar BaseResult parent: The parent ``BaseResult``.
    """

    result: Any = field(repr=True)
    parent: BaseResult = field(repr=True)

    def __call__(self) -> Any:
        return self.result


@define()
class Command(DictSerializerMixin):
    """
    A class object representing a command.

    .. warning::
        This object is meant to be used internally when
        creating new commands using the command decorators.
        Do not use this object for declaring commands.

    :ivar Callable[..., Awaitable] coro: The base command coroutine.
    :ivar ApplicationCommandType type: The type of the command.
    :ivar Optional[str] name: The name of the command. Defaults to the coroutine name.
    :ivar Optional[str] description: The description of the command. Defaults to the docstring of the coroutine or ``"No description set"``.
    :ivar Optional[List[Option]] options: The list of options for the base command.
    :ivar Optional[Union[int, Guild, List[int], List[Guild]]] scope: The scope of the command.
    :ivar Optional[str] default_member_permissions: The default member permissions of the command.
    :ivar Optional[bool] dm_permission: The DM permission of the command.
    :ivar Optional[Dict[Union[str, Locale], str]] name_localizations: The dictionary of localization for the ``name`` field. This enforces the same restrictions as the ``name`` field.
    :ivar Optional[Dict[Union[str, Locale], str]] description_localizations: The dictionary of localization for the ``description`` field. This enforces the same restrictions as the ``description`` field.
    :ivar bool default_scope: Whether the command should use the default scope. Defaults to ``True``.

    :ivar Dict[str, Callable[..., Awaitable]] coroutines: The dictionary of coroutines for the command.
    :ivar Dict[str, int] num_options: The dictionary of teh number of options per subcommand.
    :ivar Dict[str, Union[Callable[..., Awaitable], str]] autocompletions: The dictionary of autocompletions for the command.
    :ivar Optional[str] recent_group: The name of the group most recently utilized.
    :ivar bool resolved: Whether the command is synced. Defaults to ``False``.
    :ivar Extension self: The extension that the command belongs to, if any.
    """

    coro: Callable[..., Awaitable] = field()
    type: ApplicationCommandType = field(default=1, converter=ApplicationCommandType)
    name: Optional[str] = field(default=MISSING, repr=True)
    description: Optional[str] = field(default=MISSING)
    options: Optional[List[Option]] = field(converter=convert_list(Option), factory=list)
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = field(default=None)
    default_member_permissions: Optional[str] = field(default=MISSING)
    dm_permission: Optional[bool] = field(default=MISSING)
    name_localizations: Optional[Dict[Union[str, Locale], str]] = field(default=MISSING)
    description_localizations: Optional[Dict[Union[str, Locale], str]] = field(default=MISSING)
    default_scope: bool = field(default=True)

    coroutines: Dict[str, Callable[..., Awaitable]] = field(init=False, factory=dict)
    num_options: Dict[str, int] = field(init=False, factory=dict)
    autocompletions: Dict[str, Union[Callable[..., Awaitable], str]] = field(
        init=False, factory=dict
    )
    recent_group: Optional[str] = field(default=None, init=False)
    resolved: bool = field(default=False, init=False)
    self: "Extension" = field(default=None, init=False)

    def __attrs_post_init__(self) -> None:
        if self.name is MISSING:
            self.name = self.coro.__name__
        if self.description is MISSING and self.type == ApplicationCommandType.CHAT_INPUT:
            self.description = getdoc(self.coro) or "No description set"
            self.description = self.description.split("\n", 1)[0]
        if hasattr(self.coro, "_options"):
            self.options.extend(self.coro._options)
        self.coro._options = self.options
        if self.scope:
            if not isinstance(self.scope, list):
                self.scope = [self.scope]
            if any(isinstance(scope, Guild) for scope in self.scope):
                self.scope = [
                    (scope.id if isinstance(scope, Guild) else scope) for scope in self.scope
                ]
        self.scope = convert_list(int)(self.scope)
        self.num_options = {self.name: len({opt for opt in self.options if int(opt.type) > 2})}

    def __call__(self, *args, **kwargs) -> Awaitable:
        r"""
        Returns the coroutine of the command as an awaitable.

        :param \*args: Multiple positional arguments able to be passed through.
        :type \*args: tuple
        :param \**kwargs: Multiple key-word arguments able to be passed through.
        :type \**kwargs: dict
        :return: The awaitable of the command.
        :rtype: Awaitable
        """
        return self.dispatcher(*args, **kwargs)

    @property
    def full_data(self) -> Union[dict, List[dict]]:
        """
        Returns the command data in JSON format.

        :return: The command data in JSON format.
        :rtype: Union[dict, List[dict]]
        """
        from ..decor import command

        return command(
            type=self.type,
            name=self.name,
            description=self.description if self.type == 1 else MISSING,
            options=self.options if self.type == 1 else MISSING,
            scope=self.scope,
            name_localizations=self.name_localizations,
            description_localizations=self.description_localizations,
            default_member_permissions=self.default_member_permissions,
            dm_permission=self.dm_permission,
        )

    @property
    def has_subcommands(self) -> bool:
        """
        Checks if the command has subcommand options.

        :return: Whether the command has subcommand options.
        :rtype: bool
        """
        return len(self.coroutines) > 0

    def __check_options(self) -> None:
        """Checks the options to make sure they are compatible with subcommands."""
        if self.type not in (ApplicationCommandType.CHAT_INPUT, 1):
            raise LibraryException(
                code=11, message="Only chat input commands can have subcommands."
            )
        if self.options and any(
            option.type not in (OptionType.SUB_COMMAND, OptionType.SUB_COMMAND_GROUP)
            for option in self.options
        ):
            raise LibraryException(
                code=11, message="Subcommands are incompatible with base command options."
            )

    async def __no_group(self, *args, **kwargs) -> None:
        """Used when no group coroutine is provided."""
        pass

    def subcommand(
        self,
        group: Optional[str] = MISSING,
        *,
        name: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        options: Optional[List[Option]] = MISSING,
        name_localizations: Optional[Dict[Union[str, Locale], str]] = MISSING,
        description_localizations: Optional[Dict[Union[str, Locale], str]] = MISSING,
    ) -> Callable[[Callable[..., Awaitable]], "Command"]:
        """
        Creates a subcommand of the command.
        """  # TODO: change docstring

        self.__check_command()

        def decorator(coro: Callable[..., Awaitable]) -> "Command":
            _group = self.recent_group or group
            _name = coro.__name__ if name is MISSING else name
            _description = description
            if description is MISSING:
                _description = getdoc(coro) or "No description set"
                _description = _description.split("\n", 1)[0]
            _options = [] if options is MISSING else options
            if hasattr(coro, "_options"):
                _options.extend(coro._options)
            if name_localizations is MISSING:
                _name_localizations = self.name_localizations
            else:
                _name_localizations = name_localizations
            _name_localizations = None if _name_localizations is MISSING else _name_localizations
            if description_localizations is MISSING:
                _description_localizations = self.description_localizations
            else:
                _description_localizations = description_localizations
            _description_localizations = (
                None if _description_localizations is MISSING else _description_localizations
            )

            subcommand = Option(
                type=1,
                name=_name,
                description=_description,
                options=_options,
                name_localizations=_name_localizations,
                description_localizations=_description_localizations,
            )

            if _group is MISSING:
                self.options.append(subcommand)
                self.coroutines[_name] = coro
                self.num_options[_name] = len({opt for opt in _options if int(opt.type) > 2})
            else:
                for i, option in enumerate(self.options):
                    if int(option.type) == 2 and option.name == _group:
                        break
                else:
                    self.group(name=_group)(self.__no_group)
                    for i, option in enumerate(self.options):
                        if int(option.type) == 2 and option.name == _group:
                            break
                self.options[i].options.append(subcommand)
                self.options[i]._json["options"].append(subcommand._json)
                self.coroutines[f"{_group} {_name}"] = coro
                self.num_options[f"{_group} {_name}"] = len(
                    {opt for opt in _options if int(opt.type) > 2}
                )

            self.__check_options()
            return self

        return decorator

    def group(
        self,
        *,
        name: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        name_localizations: Optional[Dict[Union[str, Locale], str]] = MISSING,
        description_localizations: Optional[Dict[Union[str, Locale], str]] = MISSING,
    ) -> Callable[[Callable[..., Awaitable]], "Command"]:
        """Creates a group option"""  # TODO: change docstring

        self.__check_command()

        def decorator(coro: Callable[..., Awaitable]) -> "Command":
            _name = coro.__name__ if name is MISSING else name
            self.recent_group = _name
            _description = description
            if description is MISSING:
                _description = getdoc(coro) or "No description set"
                _description = _description.split("\n", 1)[0]
            if name_localizations is MISSING:
                _name_localizations = self.name_localizations
            else:
                _name_localizations = name_localizations
            _name_localizations = None if _name_localizations is MISSING else _name_localizations
            if description_localizations is MISSING:
                _description_localizations = self.description_localizations
            else:
                _description_localizations = description_localizations
            _description_localizations = (
                None if _description_localizations is MISSING else _description_localizations
            )
            self.coroutines[_name] = coro

            group = Option(
                type=2,
                name=_name,
                description=_description,
                options=[],
                name_localizations=_name_localizations,
                description_localizations=_description_localizations,
            )
            self.options.append(group)
            self.__check_options()

            return self

        return decorator

    async def _call(
        self,
        coro: Callable[..., Awaitable],
        ctx: "CommandContext",
        *args,
        _name: Optional[str] = None,
        _res: Optional[Union[BaseResult, GroupResult]] = None,
        **kwargs,
    ) -> Optional[Any]:
        var_len = len(coro.__code__.co_varnames)
        arg_len = self.num_options.get(_name, len(args) + len(kwargs))

        if self.self:
            if var_len < 2:
                raise LibraryException(
                    code=11,
                    message="Your command needs at least two arguments to return self and context.",
                )

            if var_len == 2:
                return await coro(self.self, ctx)

            if _res:
                if var_len - arg_len == 2:
                    return await coro(self.self, ctx, *args, **kwargs)
                elif var_len - arg_len == 3:
                    return await coro(self.self, ctx, _res, *args, **kwargs)

            return await coro(self.self, ctx, *args, **kwargs)
        else:
            if var_len < 1:
                raise LibraryException(
                    code=11, message="Your command needs at least one argument to return context."
                )

            if var_len == 1:
                return await coro(ctx)

            if _res:
                if var_len - arg_len == 1:
                    return await coro(ctx, *args, **kwargs)
                elif var_len - arg_len == 2:
                    return await coro(ctx, _res, *args, **kwargs)

            return await coro(ctx, *args, **kwargs)

    @property
    def dispatcher(self) -> Callable[..., Awaitable]:
        """
        Returns a coroutine that calls the command along with the subcommands, if any.

        :return: A coroutine that calls the command along with the subcommands, if any.
        :rtype: Callable[..., Awaitable]
        """
        if not self.has_subcommands:
            return self.__wrap_coro(self.coro)

        @wraps(self.coro)
        async def dispatch(
            ctx: "CommandContext",
            *args,
            sub_command_group: Optional[str] = None,
            sub_command: Optional[str] = None,
            **kwargs,
        ) -> Optional[Any]:
            """Dispatches all of the subcommands of the command."""
            base_coro = self.coro
            base_res = BaseResult(
                result=await self._call(base_coro, ctx, *args, _name=self.name, **kwargs)
            )
            if base_res() is StopCommand or isinstance(base_res(), StopCommand):
                return
            if sub_command_group:
                group_coro = self.coroutines[sub_command_group]
                name = f"{sub_command_group} {sub_command}"
                subcommand_coro = self.coroutines[name]
                group_res = GroupResult(
                    result=await self._call(
                        group_coro, ctx, *args, _res=base_res, _name=sub_command_group, **kwargs
                    ),
                    parent=base_res,
                )
                if group_res() is StopCommand or isinstance(group_res(), StopCommand):
                    return
                return await self._call(
                    subcommand_coro, ctx, *args, _res=group_res, _name=name, **kwargs
                )
            elif sub_command:
                subcommand_coro = self.coroutines[sub_command]
                return await self._call(
                    subcommand_coro, ctx, *args, _res=base_res, _name=sub_command, **kwargs
                )
            return base_res

        return dispatch

    def autocomplete(
        self, name: Optional[str] = MISSING
    ) -> Callable[[Callable[..., Coroutine]], Callable[..., Coroutine]]:
        """add docstring"""  # TODO: change docstring

        self.__check_command()

        def decorator(coro: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
            _name = name
            if name is MISSING:
                _name = coro.__name__

            data = {"coro": self.__wrap_coro(coro), "name": _name}

            if autocompletion := self.autocompletions.get(self.name):
                autocompletion.append(data)
            else:
                self.autocompletions[self.name] = [data]

            return coro

        return decorator

    def __check_command(self) -> None:
        if self.type != ApplicationCommandType.CHAT_INPUT:
            raise LibraryException(
                code=11, message="Autocomplete can only be used on chat input commands."
            )

    def __wrap_coro(self, coro: Callable[..., Awaitable]) -> Callable[..., Awaitable]:
        @wraps(coro)
        def wrapper(*args, **kwargs):
            return coro(self.self, *args, **kwargs) if self.self else coro(*args, **kwargs)

        return wrapper
