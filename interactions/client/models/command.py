from asyncio import CancelledError
from functools import wraps
from inspect import getdoc, signature
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Coroutine, Dict, List, Optional, Union

from ...api.error import LibraryException
from ...api.models.channel import Channel, ChannelType
from ...api.models.guild import Guild
from ...api.models.member import Member
from ...api.models.message import Attachment
from ...api.models.misc import Snowflake
from ...api.models.role import Role
from ...api.models.user import User
from ...utils.attrs_utils import DictSerializerMixin, convert_list, define, field
from ...utils.missing import MISSING
from ..enums import ApplicationCommandType, Locale, OptionType, PermissionType

if TYPE_CHECKING:
    from ...api.dispatch import Listener
    from ..bot import Client, Extension
    from ..context import CommandContext

__all__ = (
    "Choice",
    "Option",
    "Permission",
    "ApplicationCommand",
    "option",
    "StopCommand",
    "BaseResult",
    "GroupResult",
    "Command",
)


@define()
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
    :ivar Optional[int] min_length?: The minimum length supported by the option.
    :ivar Optional[int] max_length?: The maximum length supported by the option.
    :ivar Optional[bool] autocomplete?: A status denoting whether this option is an autocomplete option.
    :ivar Optional[Dict[Union[str, Locale], str]] name_localizations?: The dictionary of localization for the ``name`` field. This enforces the same restrictions as the ``name`` field.
    :ivar Optional[Dict[Union[str, Locale], str]] description_localizations?: The dictionary of localization for the ``description`` field. This enforces the same restrictions as the ``description`` field.
    :ivar Optional[str] converter: How the option value is passed to the function, if different than ``name``
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
    min_length: Optional[int] = field(default=None)
    max_length: Optional[int] = field(default=None)
    autocomplete: Optional[bool] = field(default=None)
    name_localizations: Optional[Dict[Union[str, Locale], str]] = field(
        default=None
    )  # this may backfire
    description_localizations: Optional[Dict[Union[str, Locale], str]] = field(
        default=None
    )  # so can this
    converter: Optional[str] = field(default=None)

    def __attrs_post_init__(self):
        self._json.pop("converter", None)

        # needed for nested classes
        if self.options is not None:
            self.options = [
                Option(**option) if isinstance(option, dict) else option for option in self.options
            ]
            self._json["options"] = [option._json for option in self.options]
        if self.choices is not None:
            self.choices = [
                Choice(**choice) if isinstance(choice, dict) else choice for choice in self.choices
            ]
            self._json["choices"] = [choice._json for choice in self.choices]


@define()
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
    description: str = "No description set",
    /,
    **kwargs,
) -> Callable[[Callable[..., Awaitable]], Callable[..., Awaitable]]:
    r"""
    A decorator for adding options to a command.

    The ``type`` and ``name`` of the option are defaulted to the parameter's typehint and name.

    When the ``name`` of the option differs from the parameter name,
    the ``converter`` field will default to the name of the parameter.

    The structure of an option:

    .. code-block:: python

        @client.command()
        @interactions.option("description (optional)")  # kwargs are optional, same as Option
        async def my_command(ctx, opt: str):
            ...

    :param description?: The description of the option. Defaults to "No description set".
    :type description?: str
    :param \**kwargs?: The keyword arguments of the option, same as :class:`Option`.
    :type \**kwargs?: dict
    """

    def decorator(coro: Callable[..., Awaitable]) -> Callable[..., Awaitable]:
        parameters = list(signature(coro).parameters.values())

        if not hasattr(coro, "_options") or not isinstance(coro._options, list):
            coro._options = []

        param = parameters[-1 - len(coro._options)]

        option_type = kwargs.pop("type", param.annotation)
        name = kwargs.pop("name", param.name)
        if name != param.name:
            kwargs["converter"] = param.name

        if option_type is param.empty:
            raise LibraryException(
                code=12,
                message=f"No type specified for option '{name}'.",
            )

        option_types = {
            str: OptionType.STRING,
            int: OptionType.INTEGER,
            bool: OptionType.BOOLEAN,
            User: OptionType.USER,
            Member: OptionType.USER,
            Channel: OptionType.CHANNEL,
            Role: OptionType.ROLE,
            float: OptionType.NUMBER,
            Attachment: OptionType.ATTACHMENT,
        }
        option_type = option_types.get(option_type, option_type)

        _option = Option(
            type=option_type,
            name=name,
            description=kwargs.pop("description", description),
            required=kwargs.pop("required", param.default is param.empty),
            **kwargs,
        )
        coro._options.insert(0, _option)
        return coro

    return decorator


class StopCommand:
    """
    A class that when returned from a command, the command chain is stopped.

    Usage:

    .. code-block:: python

        @bot.command()
        async def foo(ctx):
            ... # do something
            return StopCommand  # does not execute `bar`
            # or `return StopCommand()`

        @foo.subcommand()
        async def bar(ctx):
            ...  # `bar` is not executed

    This allows for custom checks that allow stopping the command chain.
    """


@define()
class BaseResult(DictSerializerMixin):
    """
    A class object representing the result of the base command.

    Usage:

    .. code-block:: python

        @bot.command()
        async def foo(ctx):
            ... # do something
            return "done"  # return something

        @foo.subcommand()
        async def bar(ctx, base_res: BaseResult):
            print(base_res.result)  # "done"

    .. note::
        If the subcommand coroutine does not have enough parameters, the ``BaseResult`` will not be passed.

    :ivar Any result: The result of the base command.
    """

    result: Any = field(repr=True)

    def __call__(self) -> Any:
        return self.result


@define()
class GroupResult(DictSerializerMixin):
    """
    A class object representing the result of the base command.

    Usage:

    .. code-block:: python

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
    :ivar Dict[str, int] num_options: The dictionary of the number of options per subcommand.
    :ivar Dict[str, Union[Callable[..., Awaitable], str]] autocompletions: The dictionary of autocompletions for the command.
    :ivar Optional[str] recent_group: The name of the group most recently utilized.
    :ivar bool resolved: Whether the command is synced. Defaults to ``False``.
    :ivar Optional[Extension] extension: The extension that the command belongs to, if any.
    :ivar Client client: The client that the command belongs to.
    :ivar Optional[Listener] listener: The listener, used for dispatching command errors.
    """

    coro: Callable[..., Awaitable] = field()
    type: ApplicationCommandType = field(default=1, converter=ApplicationCommandType)
    name: Optional[str] = field(default=MISSING, repr=True)
    description: Optional[str] = field(default=MISSING)
    options: Optional[List[Option]] = field(converter=convert_list(Option), factory=list)
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = field(default=MISSING)
    default_member_permissions: Optional[str] = field(default=MISSING)
    dm_permission: Optional[bool] = field(default=MISSING)
    name_localizations: Optional[Dict[Union[str, Locale], str]] = field(default=MISSING)
    description_localizations: Optional[Dict[Union[str, Locale], str]] = field(default=MISSING)
    default_scope: bool = field(default=True)

    coroutines: Dict[str, Callable[..., Awaitable]] = field(init=False, factory=dict)
    num_options: Dict[str, int] = field(init=False, factory=dict)
    autocompletions: Dict[str, List[Union[Callable[..., Awaitable], str]]] = field(
        init=False, factory=dict
    )
    recent_group: Optional[str] = field(default=None, init=False)
    error_callback: Optional[Callable[..., Awaitable]] = field(default=None, init=False)
    resolved: bool = field(default=False, init=False)
    extension: Optional["Extension"] = field(default=None, init=False)
    client: "Client" = field(default=None, init=False)
    listener: Optional["Listener"] = field(default=None, init=False)

    def __attrs_post_init__(self) -> None:
        if self.name is MISSING:
            self.name = self.coro.__name__
        if self.description is MISSING and self.type == ApplicationCommandType.CHAT_INPUT:
            self.description = getdoc(self.coro) or "No description set"
            self.description = self.description.split("\n", 1)[0]
        if hasattr(self.coro, "_options"):
            self.options.extend(self.coro._options)
        self.coro._options = self.options
        if self.scope and self.scope is not MISSING:
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
    def converters(self) -> dict:
        """
        Returns a dictionary with all converters added to the options of the command
        """
        return {_option.name: _option.converter for _option in self.options if _option.converter}

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
        Decorator for creating a subcommand of the command.

        The structure for a subcommand:

        .. code-block:: python

            @bot.command()
            async def base_command(ctx):
                pass  # do whatever you want here

            @base_command.subcommand()
            async def subcommand(ctx):
                pass  # do whatever you want here
                # you can also have a parameter for the base result

            @base_command.subcommand("group_name")
            async def subcommand_group(ctx):
                pass  # you can decide to create a subcommand group
                      # without creating a group, like this

        .. note::
            If you want to create both subcommands and subcommands with groups,
            first create the subcommands without groups, then create the subcommands with groups.

        :param group?: The name of the group the subcommand belongs to. Defaults to the most recently used group.
        :type group?: Optional[str]
        :param name?: The name of the subcommand. Defaults to the name of the coroutine.
        :type name?: Optional[str]
        :param description?: The description of the subcommand. Defaults to the docstring of the coroutine.
        :type description?: Optional[str]
        :param options?: The options of the subcommand.
        :type options?: Optional[List[Option]]
        :param name_localizations?: The dictionary of localization for the ``name`` field. This enforces the same restrictions as the ``name`` field.
        :type name_localizations?: Optional[Dict[Union[str, Locale], str]]
        :param description_localizations?: The dictionary of localization for the ``description`` field. This enforces the same restrictions as the ``description`` field.
        :type description_localizations?: Optional[Dict[Union[str, Locale], str]]
        :return: The :class:`interactions.client.models.command.Command` object.
        :rtype: Command
        """

        self.__check_command("subcommand")

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
                self.coroutines[_name] = self.__wrap_coro(coro)
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
                self.coroutines[f"{_group} {_name}"] = self.__wrap_coro(coro)
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
        """
        Decorator for creating a group of the command.

        The structure for a group:

        .. code-block:: python

            @bot.command()
            async def base_command(ctx):
                pass

            @base_command.group()
            async def group(ctx):
                \"""description\"""
                pass  # you can also have a parameter for the base result

            @group.subcommand()
            async def subcommand_group(ctx):
                pass

        .. note::
            If you want to create both subcommands and subcommands with groups,
            first create the subcommands without groups, then create the subcommands with groups.

        :param name?: The name of the group. Defaults to the name of the coroutine.
        :type name?: Optional[str]
        :param description?: The description of the group. Defaults to the docstring of the coroutine.
        :type description?: Optional[str]
        :param name_localizations?: The dictionary of localization for the ``name`` field. This enforces the same restrictions as the ``name`` field.
        :type name_localizations?: Optional[Dict[Union[str, Locale], str]]
        :param description_localizations?: The dictionary of localization for the ``description`` field. This enforces the same restrictions as the ``description`` field.
        :type description_localizations?: Optional[Dict[Union[str, Locale], str]]
        :return: The :class:`interactions.client.models.command.Command` object.
        :rtype: Command
        """

        self.__check_command("group")

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
            self.coroutines[_name] = self.__wrap_coro(coro)

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

    @property
    def dispatcher(self) -> Callable[..., Awaitable]:
        """
        Returns a coroutine that calls the command along with the subcommands, if any.

        .. note::
            The coroutine returned is never the same object.

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
                result=await self.__call(base_coro, ctx, *args, _name=self.name, **kwargs)
            )
            if base_res() is StopCommand or isinstance(base_res(), StopCommand):
                return
            if sub_command_group:
                group_coro = self.coroutines[sub_command_group]
                name = f"{sub_command_group} {sub_command}"
                subcommand_coro = self.coroutines[name]
                group_res = GroupResult(
                    result=await self.__call(
                        group_coro, ctx, *args, _res=base_res, _name=sub_command_group, **kwargs
                    ),
                    parent=base_res,
                )
                if group_res() is StopCommand or isinstance(group_res(), StopCommand):
                    return
                return await self.__call(
                    subcommand_coro, ctx, *args, _res=group_res, _name=name, **kwargs
                )
            elif sub_command:
                subcommand_coro = self.coroutines[sub_command]
                return await self.__call(
                    subcommand_coro, ctx, *args, _res=base_res, _name=sub_command, **kwargs
                )
            return base_res

        return dispatch

    def autocomplete(
        self, name: Optional[str] = MISSING
    ) -> Callable[[Callable[..., Coroutine]], Callable[..., Coroutine]]:
        """
        Decorator for creating an autocomplete for the command.

        :param name?: The name of the option to autocomplete. Defaults to the name of the coroutine.
        :type name?: Optional[str]
        :return: The coroutine
        :rtype: Callable[..., Coroutine]
        """

        self.__check_command("autocomplete")

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

    def error(self, coro: Callable[..., Coroutine], /) -> Callable[..., Coroutine]:
        """
        Decorator for assigning a callback coroutine to be called when an error occurs.

        The structure of the decorator:

        .. code-block:: python

            @bot.command()
            async def command(ctx):
                raise Exception("Error")  # example error

            @command.error
            async def command_error(ctx, error):
                ...  # do something with the error

        .. note::
            The context and error are required as parameters,
            but you can also have additional parameters so that the
            base or group result (if any) and/or options are passed.

        :param coro: The coroutine to be called when an error occurs.
        :type coro: Callable[..., Coroutine]
        """
        num_params = len(signature(coro).parameters)

        if num_params < (3 if self.extension else 2):
            raise LibraryException(
                code=11,
                message=f"Your command needs at least {'three parameters to return self, context, and the' if self.extension else 'two parameter to return context and'} error.",
            )

        self.error_callback = self.__wrap_coro(coro, error_callback=True)
        return coro

    async def __call(
        self,
        coro: Callable[..., Awaitable],
        ctx: "CommandContext",
        *args,  # empty for now since all parameters are dispatched as kwargs
        _name: Optional[str] = None,
        _res: Optional[Union[BaseResult, GroupResult]] = None,
        **kwargs,
    ) -> Optional[Any]:
        """Handles calling the coroutine based on parameter count."""
        params = signature(coro).parameters
        param_len = len(params)
        opt_len = self.num_options.get(_name, len(args) + len(kwargs))  # options of slash command
        last = params[list(params)[-1]]  # last parameter
        has_args = any(param.kind == param.VAR_POSITIONAL for param in params.values())  # any *args
        index_of_var_pos = next(
            (i for i, param in enumerate(params.values()) if param.kind == param.VAR_POSITIONAL),
            param_len,
        )  # index of *args
        par_opts = list(params.keys())[
            (num := 2 if self.extension else 1) : (
                -1 if last.kind in (last.VAR_POSITIONAL, last.VAR_KEYWORD) else index_of_var_pos
            )
        ]  # parameters that are before *args and **kwargs
        keyword_only_args = list(params.keys())[index_of_var_pos:]  # parameters after *args

        try:
            _coro = coro if hasattr(coro, "_wrapped") else self.__wrap_coro(coro)

            if last.kind == last.VAR_KEYWORD:  # foo(ctx, ..., **kwargs)
                return await _coro(ctx, *args, **kwargs)
            if last.kind == last.VAR_POSITIONAL:  # foo(ctx, ..., *args)
                return await _coro(
                    ctx,
                    *(kwargs[opt] for opt in par_opts if opt in kwargs),
                    *args,
                )
            if has_args:  # foo(ctx, ..., *args, ..., **kwargs) OR foo(ctx, *args, ...)
                return await _coro(
                    ctx,
                    *(kwargs[opt] for opt in par_opts if opt in kwargs),  # pos before *args
                    *args,
                    *(
                        kwargs[opt]
                        for opt in kwargs
                        if opt not in par_opts and opt not in keyword_only_args
                    ),  # additional args
                    **{
                        opt: kwargs[opt]
                        for opt in kwargs
                        if opt not in par_opts and opt in keyword_only_args
                    },  # kwargs after *args
                )

            if param_len < num:
                inner_msg: str = f"{num} parameter{'s' if num > 1 else ''} to return" + (
                    " self and" if self.extension else ""
                )
                raise LibraryException(
                    code=11, message=f"Your command needs at least {inner_msg} context."
                )

            if param_len == num:
                return await _coro(ctx)

            if _res:
                if param_len - opt_len == num:
                    return await _coro(ctx, *args, **kwargs)
                elif param_len - opt_len == num + 1:
                    return await _coro(ctx, _res, *args, **kwargs)

            return await _coro(ctx, *args, **kwargs)
        except CancelledError:
            pass

    def __check_command(self, command_type: str) -> None:
        """Checks if subcommands, groups, or autocompletions are created on context menus."""
        if self.type != ApplicationCommandType.CHAT_INPUT:
            raise LibraryException(
                code=11, message=f"{command_type} can only be used on chat input commands."
            )

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
        """This is the coroutine used when no group coroutine is provided."""
        pass

    def __wrap_coro(
        self, coro: Callable[..., Awaitable], /, *, error_callback: bool = False
    ) -> Callable[..., Awaitable]:
        """Wraps a coroutine to make sure the :class:`interactions.client.bot.Extension` is passed to the coroutine, if any."""

        @wraps(coro)
        async def wrapper(ctx: "CommandContext", *args, **kwargs):
            ctx.client = self.client
            ctx.command = self
            ctx.extension = self.extension

            try:
                if self.extension:
                    return await coro(self.extension, ctx, *args, **kwargs)
                return await coro(ctx, *args, **kwargs)
            except CancelledError:
                pass
            except Exception as e:
                if error_callback:
                    raise e
                if self.error_callback:
                    params = signature(self.error_callback).parameters
                    num_params = len(params)
                    last = params[list(params)[-1]]
                    num = 2 if self.extension else 1

                    if num_params == num:
                        await self.error_callback(ctx)
                    elif num_params == num + 1:
                        await self.error_callback(ctx, e)
                    elif last.kind == last.VAR_KEYWORD:
                        if num_params == num + 2:
                            await self.error_callback(ctx, e, **kwargs)
                        elif num_params >= num + 3:
                            await self.error_callback(ctx, e, *args, **kwargs)
                    elif last.kind == last.VAR_POSITIONAL:
                        if num_params == num + 2:
                            await self.error_callback(ctx, e, *args)
                        elif num_params >= num + 3:
                            await self.error_callback(ctx, e, *args, **kwargs)
                    else:
                        await self.error_callback(ctx, e, *args, **kwargs)
                elif self.listener and "on_command_error" in self.listener.events:
                    self.listener.dispatch("on_command_error", ctx, e)
                else:
                    raise e

                return StopCommand

        wrapper._wrapped = True
        return wrapper
