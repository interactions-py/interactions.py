import asyncio
import functools
import inspect
from typing import Any, Callable, Coroutine, TYPE_CHECKING, Optional, TypeGuard

import attrs

from interactions.client.const import Absent, GLOBAL_SCOPE, MISSING, T
from interactions.client.errors import BadArgument
from interactions.client.utils.misc_utils import get_object_name, maybe_coroutine
from interactions.models.internal.application_commands import (
    SlashCommand,
    LocalisedName,
    LocalisedDesc,
    SlashCommandOption,
    SlashCommandChoice,
    OptionTypes,
)
from interactions.models.internal.command import BaseCommand
from interactions.models.internal.context import HybridContext, InteractionContext, PrefixedContext
from interactions.models.internal.converters import (
    _LiteralConverter,
    NoArgumentConverter,
    MemberConverter,
    UserConverter,
    RoleConverter,
    BaseChannelConverter,
)
from interactions.models.internal.prefixed_commands import _convert_to_bool, PrefixedCommand
from interactions.models.internal.protocols import Converter

if TYPE_CHECKING:
    from interactions.models.internal.checks import TYPE_CHECK_FUNCTION
    from interactions.models.discord.channel import BaseChannel
    from interactions.models.discord.message import Attachment
    from interactions.models.discord.enums import Permissions, ChannelTypes
    from interactions.models.discord.snowflake import Snowflake_Type

__all__ = ("HybridCommand", "hybrid_command", "hybrid_subcommand")

_get_converter_function = BaseCommand._get_converter_function


def _check_if_annotation(param_annotation: Any, type_: type[T]) -> TypeGuard[T]:
    return (
        isinstance(param_annotation, type_) or inspect.isclass(param_annotation) and issubclass(param_annotation, type_)
    )


def _create_subcmd_func(group: bool = False) -> Callable:
    async def _subcommand_base(*args, **kwargs) -> None:
        if group:
            raise BadArgument("Cannot run this subcommand group without a valid subcommand.")
        else:
            raise BadArgument("Cannot run this command without a valid subcommand.")

    return _subcommand_base


def _generate_permission_check(permissions: "Permissions") -> "TYPE_CHECK_FUNCTION":
    async def _permission_check(ctx: HybridContext) -> bool:
        return ctx.author.has_permission(*permissions) if ctx.guild_id else True  # type: ignore

    return _permission_check  # type: ignore


def _generate_scope_check(_scopes: list["Snowflake_Type"]) -> "TYPE_CHECK_FUNCTION":
    scopes = frozenset(int(s) for s in _scopes)

    async def _scope_check(ctx: HybridContext) -> bool:
        return int(ctx.guild_id) in scopes

    return _scope_check  # type: ignore


async def _guild_check(ctx: HybridContext) -> bool:
    return bool(ctx.guild_id)


def _match_option_type(option_type: int) -> Callable[[HybridContext, Any], Any]:
    if option_type == 3:
        return lambda ctx, arg: str(arg)
    if option_type == 4:
        return lambda ctx, arg: int(arg)
    if option_type == 5:
        return lambda ctx, arg: _convert_to_bool(arg)
    if option_type == 6:
        return _get_converter_function(_UnionConverter(MemberConverter, UserConverter), "")
    if option_type == 7:
        return _get_converter_function(BaseChannelConverter, "")
    if option_type == 8:
        return _get_converter_function(RoleConverter, "")
    if option_type == 9:
        return _get_converter_function(_UnionConverter(MemberConverter, UserConverter, RoleConverter), "")
    if option_type == 10:
        return lambda ctx, arg: float(arg)
    if option_type == 11:
        return _BasicAttachmentConverter  # type: ignore

    raise ValueError(f"{option_type} is an unsupported option type right now.")


class _UnionConverter(Converter):
    def __init__(self, *converters: type[Converter]) -> None:
        self._converters = converters

    async def convert(self, ctx: HybridContext, arg: Any) -> Any:
        for converter in self._converters:
            try:
                return await converter().convert(ctx, arg)
            except Exception:  # noqa
                continue

        union_names = tuple(get_object_name(t).removesuffix("Converter") for t in self._converters)
        union_types_str = ", ".join(union_names[:-1]) + f", or {union_names[-1]}"
        raise BadArgument(f'Could not convert "{arg}" into {union_types_str}.')


class _BasicAttachmentConverter(NoArgumentConverter):
    def convert(self, ctx: HybridContext, _: Any) -> "Attachment":
        try:
            return ctx.message.attachments[0]
        except (AttributeError, IndexError):
            raise BadArgument("No attachment found.") from None


class _ChoicesConverter(_LiteralConverter):
    values: dict
    choice_values: dict

    def __init__(self, choices: list[SlashCommandChoice | dict]) -> None:
        standardized_choices = tuple((SlashCommandChoice(**o) if isinstance(o, dict) else o) for o in choices)

        names = tuple(c.name for c in standardized_choices)
        self.values = {str(arg): str for arg in names}
        self.choice_values = {str(c.name): c.value for c in standardized_choices}

    async def convert(self, ctx: HybridContext, argument: str) -> Any:
        val = await super().convert(ctx, argument)
        return self.choice_values[val]


class _StringLengthConverter(Converter[str]):
    def __init__(self, min_length: Optional[int], max_length: Optional[int]) -> None:
        self.min_length = min_length
        self.max_length = max_length

    async def convert(self, ctx: HybridContext, argument: str) -> str:
        if self.min_length and len(argument) < self.min_length:
            raise BadArgument(f'The string "{argument}" is shorter than {self.min_length} character(s).')
        elif self.max_length and len(argument) > self.max_length:
            raise BadArgument(f'The string "{argument}" is longer than {self.max_length} character(s).')

        return argument


class _RangeConverter(Converter[float | int]):
    def __init__(
        self,
        number_convert: Callable[[HybridContext, Any], Any],
        number_type: int,
        min_value: Optional[float | int],
        max_value: Optional[float | int],
    ) -> None:
        self.number_convert = number_convert
        self.number_type = number_type
        self.min_value = min_value
        self.max_value = max_value

    async def convert(self, ctx: HybridContext, argument: str) -> float | int:
        try:
            converted: float | int = await maybe_coroutine(self.number_convert, ctx, argument)

            if self.min_value and converted < self.min_value:
                raise BadArgument(f'Value "{argument}" is less than {self.min_value}.')
            if self.max_value and converted > self.max_value:
                raise BadArgument(f'Value "{argument}" is greater than {self.max_value}.')

            return converted
        except ValueError:
            type_name = "number" if self.number_type == OptionTypes.NUMBER else "integer"

            if type_name.startswith("i"):
                raise BadArgument(f'Argument "{argument}" is not an {type_name}.') from None
            else:
                raise BadArgument(f'Argument "{argument}" is not a {type_name}.') from None
        except BadArgument:
            raise


class _NarrowedChannelConverter(BaseChannelConverter):
    def __init__(self, channel_types: "list[ChannelTypes | int]") -> None:
        self.channel_types = channel_types

    async def convert(self, ctx: HybridContext, argument: str) -> "BaseChannel":
        channel = await super().convert(ctx, argument)
        if channel.type not in self.channel_types:
            raise BadArgument(f'Channel "{channel.mention}" is not an allowed channel type.')
        return channel


class _StackedConverter(Converter):
    def __init__(
        self,
        ori_converter_func: Callable[[HybridContext, Any], Any],
        additional_converter_func: Callable[[HybridContext, Any], Any],
    ) -> None:
        self._ori_converter_func = ori_converter_func
        self._additional_converter_func = additional_converter_func

    async def convert(self, ctx: HybridContext, argument: Any) -> Any:
        part_one = await maybe_coroutine(self._ori_converter_func, ctx, argument)
        return await maybe_coroutine(self._additional_converter_func, ctx, part_one)


class _StackedNoArgConverter(NoArgumentConverter):
    def __init__(
        self,
        ori_converter_func: Callable[[HybridContext, Any], Any],
        additional_converter_func: Callable[[HybridContext, Any], Any],
    ) -> None:
        self._ori_converter_func = ori_converter_func
        self._additional_converter_func = additional_converter_func

    async def convert(self, ctx: HybridContext, _: Any) -> Any:
        part_one = await maybe_coroutine(self._ori_converter_func, ctx, _)
        return await maybe_coroutine(self._additional_converter_func, ctx, part_one)


@attrs.define(eq=False, order=False, hash=False, kw_only=True)
class HybridCommand(SlashCommand):
    """A subclass of SlashCommand that handles the logic for hybrid commands."""

    async def __call__(self, context: InteractionContext, *args, **kwargs) -> None:
        new_ctx = context.bot.hybrid_context.from_interaction_context(context)
        return await super().__call__(new_ctx, *args, **kwargs)

    def group(self, name: str = None, description: str = "No Description Set") -> "HybridCommand":
        return HybridCommand(
            name=self.name,
            description=self.description,
            group_name=name,
            group_description=description,
            scopes=self.scopes,
        )

    def subcommand(
        self,
        sub_cmd_name: LocalisedName | str,
        group_name: LocalisedName | str = None,
        sub_cmd_description: Absent[LocalisedDesc | str] = MISSING,
        group_description: Absent[LocalisedDesc | str] = MISSING,
        options: list[SlashCommandOption | dict] = None,
        nsfw: bool = False,
    ) -> Callable[..., "HybridCommand"]:
        def wrapper(call: Callable[..., Coroutine]) -> "HybridCommand":
            nonlocal sub_cmd_description

            if not asyncio.iscoroutinefunction(call):
                raise TypeError("Subcommand must be coroutine")

            if sub_cmd_description is MISSING:
                sub_cmd_description = call.__doc__ or "No Description Set"

            return HybridCommand(
                name=self.name,
                description=self.description,
                group_name=group_name or self.group_name,
                group_description=group_description or self.group_description,
                sub_cmd_name=sub_cmd_name,
                sub_cmd_description=sub_cmd_description,
                default_member_permissions=self.default_member_permissions,
                dm_permission=self.dm_permission,
                options=options,
                callback=call,
                scopes=self.scopes,
                nsfw=nsfw,
            )

        return wrapper


@attrs.define(eq=False, order=False, hash=False, kw_only=True)
class _HybridPrefixedCommand(PrefixedCommand):
    _uses_subcommand_func: bool = attrs.field(repr=False, default=False)

    async def __call__(self, context: PrefixedContext, *args, **kwargs) -> None:
        new_ctx = context.bot.hybrid_context.from_prefixed_context(context)
        return await super().__call__(new_ctx, *args, **kwargs)

    def add_command(self, cmd: "_HybridPrefixedCommand") -> None:
        super().add_command(cmd)

        if not self._uses_subcommand_func:
            self.callback = _create_subcmd_func(group=self.is_subcommand)
            self.parameters = []
            self.ignore_extra = False
            self._inspect_signature = inspect.Signature(None)
            self._uses_subcommand_func = True


def _base_subcommand_generator(
    name: str, aliases: list[str], description: str, group: bool = False
) -> _HybridPrefixedCommand:
    return _HybridPrefixedCommand(
        callback=_create_subcmd_func(group=group),
        name=name,
        aliases=aliases,
        help=description,
        ignore_extra=False,
        inspect_signature=inspect.Signature(None),  # type: ignore
    )


def _prefixed_from_slash(cmd: SlashCommand) -> _HybridPrefixedCommand:
    new_parameters: list[inspect.Parameter] = []

    if cmd.options:
        if cmd.has_binding:
            old_func = functools.partial(cmd.callback, None, None)
        else:
            old_func = functools.partial(cmd.callback, None)

        old_params = dict(inspect.signature(old_func).parameters)
        attachment_option = False

        standardized_options = ((SlashCommandOption(**o) if isinstance(o, dict) else o) for o in cmd.options)
        for option in standardized_options:
            annotation = _match_option_type(option.type)

            if option.type == OptionTypes.ATTACHMENT:
                if attachment_option:
                    raise ValueError("Cannot have multiple attachment options.")
                else:
                    attachment_option = True

            if option.autocomplete:
                # there isn't much we can do here
                raise ValueError("Cannot use autocomplete in hybrid commands.")

            if option.type in {OptionTypes.STRING, OptionTypes.INTEGER, OptionTypes.NUMBER} and option.choices:
                annotation = _ChoicesConverter(option.choices).convert
            elif option.type in {OptionTypes.INTEGER, OptionTypes.NUMBER} and (
                option.min_value is not None or option.max_value is not None
            ):
                annotation = _RangeConverter(annotation, option.type, option.min_value, option.max_value).convert
            elif option.type == OptionTypes.STRING and (option.min_length is not None or option.max_length is not None):
                annotation = _StringLengthConverter(option.min_length, option.max_length).convert
            elif option.type == OptionTypes.CHANNEL and option.channel_types:
                annotation = _NarrowedChannelConverter(option.channel_types).convert

            if ori_param := old_params.pop(str(option.name), None):
                if ori_param.annotation != inspect._empty and _check_if_annotation(ori_param.annotation, Converter):
                    if option.type != OptionTypes.ATTACHMENT:
                        annotation = _StackedConverter(annotation, _get_converter_function(ori_param.annotation, str(option.name)))  # type: ignore
                    else:
                        annotation = _StackedNoArgConverter(_get_converter_function(annotation, ""), _get_converter_function(ori_param.annotation, str(option.name)))  # type: ignore

                if not option.required and ori_param.default == inspect._empty:
                    # prefixed commands would automatically fill this in, slash commands don't
                    # technically, there would be an error for this, but it would
                    # be unclear
                    raise ValueError("Optional options must have a default value.")

                default = inspect._empty if option.required else ori_param.default
            else:
                # in case they use something like **kwargs, though this isn't a perfect solution
                default = inspect._empty if option.required else None

            new_parameters.append(
                inspect.Parameter(
                    str(option.name),
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=default,
                    annotation=annotation,
                )
            )

        new_parameters.extend(
            inspect.Parameter(
                str(remaining_param.name),
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=remaining_param.default,
                annotation=remaining_param.annotation,
            )
            for remaining_param in old_params.values()
            if _check_if_annotation(remaining_param.annotation, NoArgumentConverter)
        )

    prefixed_cmd = _HybridPrefixedCommand(
        name=str(cmd.sub_cmd_name) if cmd.is_subcommand else str(cmd.name),
        aliases=list(cmd.sub_cmd_name.to_locale_dict().values())
        if cmd.is_subcommand
        else list(cmd.name.to_locale_dict().values()),
        help=str(cmd.sub_cmd_description) if cmd.is_subcommand else str(cmd.description),
        callback=cmd.callback,
        extension=cmd.extension,
        inspect_signature=inspect.Signature(new_parameters),  # type: ignore
    )

    if cmd.has_binding:
        prefixed_cmd._binding = cmd._binding

    if not cmd.is_subcommand:
        # these mean nothing in subcommands
        if cmd.scopes != [GLOBAL_SCOPE]:
            prefixed_cmd.checks.append(_generate_scope_check(cmd.scopes))
        if cmd.default_member_permissions:
            prefixed_cmd.checks.append(_generate_permission_check(cmd.default_member_permissions))
        if cmd.dm_permission is False:
            prefixed_cmd.checks.append(_guild_check)

    return prefixed_cmd


def hybrid_command(
    name: str | LocalisedName,
    *,
    description: Absent[str | LocalisedDesc] = MISSING,
    scopes: Absent[list["Snowflake_Type"]] = MISSING,
    options: Optional[list[SlashCommandOption | dict]] = None,
    default_member_permissions: Optional["Permissions"] = None,
    dm_permission: bool = True,
    sub_cmd_name: str | LocalisedName = None,
    group_name: str | LocalisedName = None,
    sub_cmd_description: str | LocalisedDesc = "No Description Set",
    group_description: str | LocalisedDesc = "No Description Set",
    nsfw: bool = False,
) -> Callable[[Callable[..., Coroutine]], HybridCommand]:
    """
    A decorator to declare a coroutine as a hybrid command.

    Hybrid commands are a slash command that can also function as a prefixed command.
    These use a HybridContext instead of an InteractionContext, but otherwise are mostly identical to normal slash commands.

    Note that hybrid commands do not support autocompletes.
    They also only partially support attachments, allowing one attachment option for a command.

    note:
        While the base and group descriptions aren't visible in the discord client, currently.
        We strongly advise defining them anyway, if you're using subcommands, as Discord has said they will be visible in
        one of the future ui updates.
        They are also visible as the description for their prefixed command counterparts.

    Args:
        name: 1-32 character name of the command
        description: 1-100 character description of the command
        scopes: The scope this command exists within
        options: The parameters for the command, max 25
        default_member_permissions: What permissions members need to have by default to use this command.
        dm_permission: Should this command be available in DMs.
        sub_cmd_name: 1-32 character name of the subcommand
        sub_cmd_description: 1-100 character description of the subcommand
        group_name: 1-32 character name of the group
        group_description: 1-100 character description of the group
        nsfw: This command should only work in NSFW channels

    Returns:
        HybridCommand Object

    """

    def wrapper(func: Callable[..., Coroutine]) -> HybridCommand:
        if not asyncio.iscoroutinefunction(func):
            raise ValueError("Commands must be coroutines")

        perm = default_member_permissions
        if hasattr(func, "default_member_permissions"):
            if perm:
                perm = perm | func.default_member_permissions
            else:
                perm = func.default_member_permissions

        _description = description
        if _description is MISSING:
            _description = func.__doc__ or "No Description Set"

        return HybridCommand(
            name=name,
            group_name=group_name,
            group_description=group_description,
            sub_cmd_name=sub_cmd_name,
            sub_cmd_description=sub_cmd_description,
            description=_description,
            scopes=scopes or [GLOBAL_SCOPE],
            default_member_permissions=perm,
            dm_permission=dm_permission,
            callback=func,
            options=options,
            nsfw=nsfw,
        )

    return wrapper


def hybrid_subcommand(
    base: str | LocalisedName,
    *,
    subcommand_group: Optional[str | LocalisedName] = None,
    name: Optional[str | LocalisedName] = None,
    description: Absent[str | LocalisedDesc] = MISSING,
    base_description: Optional[str | LocalisedDesc] = None,
    base_desc: Optional[str | LocalisedDesc] = None,
    base_default_member_permissions: Optional["Permissions"] = None,
    base_dm_permission: bool = True,
    subcommand_group_description: Optional[str | LocalisedDesc] = None,
    sub_group_desc: Optional[str | LocalisedDesc] = None,
    scopes: list["Snowflake_Type"] = None,
    options: list[dict] = None,
    nsfw: bool = False,
) -> Callable[[Coroutine], HybridCommand]:
    """
    A decorator specifically tailored for creating hybrid subcommands.

    See the hybrid_command decorator for more information.

    Args:
        base: The name of the base command
        subcommand_group: The name of the subcommand group, if any.
        name: The name of the subcommand, defaults to the name of the coroutine.
        description: The description of the subcommand
        base_description: The description of the base command
        base_desc: An alias of `base_description`
        base_default_member_permissions: What permissions members need to have by default to use this command.
        base_dm_permission: Should this command be available in DMs.
        subcommand_group_description: Description of the subcommand group
        sub_group_desc: An alias for `subcommand_group_description`
        scopes: The scopes of which this command is available, defaults to GLOBAL_SCOPE
        options: The options for this command
        nsfw: This command should only work in NSFW channels

    Returns:
        A HybridCommand object

    """

    def wrapper(func) -> HybridCommand:
        if not asyncio.iscoroutinefunction(func):
            raise ValueError("Commands must be coroutines")

        _description = description
        if _description is MISSING:
            _description = func.__doc__ or "No Description Set"

        return HybridCommand(
            name=base,
            description=(base_description or base_desc) or "No Description Set",
            group_name=subcommand_group,
            group_description=(subcommand_group_description or sub_group_desc) or "No Description Set",
            sub_cmd_name=name,
            sub_cmd_description=_description,
            default_member_permissions=base_default_member_permissions,
            dm_permission=base_dm_permission,
            scopes=scopes or [GLOBAL_SCOPE],
            callback=func,
            options=options,
            nsfw=nsfw,
        )

    return wrapper
