import asyncio
import inspect
from typing import Any, Callable, List, Optional, Union, TYPE_CHECKING, Awaitable, Annotated, get_origin, get_args

import attrs
from interactions import (
    BaseContext,
    Converter,
    ConsumeRest,
    NoArgumentConverter,
    Attachment,
    SlashCommandChoice,
    OptionType,
    BaseChannelConverter,
    ChannelType,
    BaseChannel,
    MemberConverter,
    UserConverter,
    RoleConverter,
    SlashCommand,
    SlashContext,
    Absent,
    LocalisedName,
    LocalisedDesc,
    MISSING,
    SlashCommandOption,
    Snowflake_Type,
    Permissions,
)
from interactions.client.const import AsyncCallable, GLOBAL_SCOPE
from interactions.client.utils.serializer import no_export_meta
from interactions.client.utils.misc_utils import maybe_coroutine, get_object_name
from interactions.client.errors import BadArgument
from interactions.ext.prefixed_commands import PrefixedCommand, PrefixedContext
from interactions.models.internal.converters import _LiteralConverter, CONSUME_REST_MARKER
from interactions.models.internal.checks import guild_only

if TYPE_CHECKING:
    from .context import HybridContext

__all__ = ("HybridSlashCommand", "hybrid_slash_command", "hybrid_slash_subcommand")


def _values_wrapper(a_dict: dict | None) -> list:
    return list(a_dict.values()) if a_dict else []


def generate_permission_check(permissions: "Permissions") -> Callable[["HybridContext"], Awaitable[bool]]:
    async def _permission_check(ctx: "HybridContext") -> bool:
        return ctx.author.has_permission(*permissions) if ctx.guild_id else True  # type: ignore

    return _permission_check  # type: ignore


def generate_scope_check(_scopes: list["Snowflake_Type"]) -> Callable[["HybridContext"], Awaitable[bool]]:
    scopes = frozenset(int(s) for s in _scopes)

    async def _scope_check(ctx: "HybridContext") -> bool:
        return int(ctx.guild_id) in scopes

    return _scope_check  # type: ignore


class BasicConverter(Converter):
    def __init__(self, type_to_convert: Any) -> None:
        self.type_to_convert = type_to_convert

    async def convert(self, ctx: BaseContext, arg: str) -> Any:
        return self.type_to_convert(arg)


class BoolConverter(Converter):
    async def convert(self, ctx: BaseContext, argument: str) -> bool:
        lowered = argument.lower()
        if lowered in {"yes", "y", "true", "t", "1", "enable", "on"}:
            return True
        elif lowered in {"no", "n", "false", "f", "0", "disable", "off"}:  # noqa: RET505
            return False
        raise BadArgument(f"{argument} is not a recognised boolean option.")


class AttachmentConverter(NoArgumentConverter):
    async def convert(self, ctx: "HybridContext", _: Any) -> Attachment:
        try:
            attachment = ctx.message.attachments[ctx.__attachment_index__]
            ctx.__attachment_index__ += 1
            return attachment
        except IndexError:
            raise BadArgument("No attachment found.") from None


class ChoicesConverter(_LiteralConverter):
    def __init__(self, choices: list[SlashCommandChoice | dict]) -> None:
        standardized_choices = tuple((SlashCommandChoice(**o) if isinstance(o, dict) else o) for o in choices)

        names = tuple(c.name for c in standardized_choices)
        self.values = {str(arg): str for arg in names}
        self.choice_values = {str(c.name): c.value for c in standardized_choices}

    async def convert(self, ctx: BaseContext, argument: str) -> Any:
        val = await super().convert(ctx, argument)
        return self.choice_values[val]


class RangeConverter(Converter[float | int]):
    def __init__(
        self,
        number_type: int,
        min_value: Optional[float | int],
        max_value: Optional[float | int],
    ) -> None:
        self.number_type = number_type
        self.min_value = min_value
        self.max_value = max_value

        self.number_convert = int if number_type == OptionType.INTEGER else float

    async def convert(self, ctx: BaseContext, argument: str) -> float | int:
        try:
            converted: float | int = await maybe_coroutine(self.number_convert, ctx, argument)

            if self.min_value and converted < self.min_value:
                raise BadArgument(f'Value "{argument}" is less than {self.min_value}.')
            if self.max_value and converted > self.max_value:
                raise BadArgument(f'Value "{argument}" is greater than {self.max_value}.')

            return converted
        except ValueError:
            type_name = "number" if self.number_type == OptionType.NUMBER else "integer"

            if type_name.startswith("i"):
                raise BadArgument(f'Argument "{argument}" is not an {type_name}.') from None
            raise BadArgument(f'Argument "{argument}" is not a {type_name}.') from None
        except BadArgument:
            raise


class StringLengthConverter(Converter[str]):
    def __init__(self, min_length: Optional[int], max_length: Optional[int]) -> None:
        self.min_length = min_length
        self.max_length = max_length

    async def convert(self, ctx: BaseContext, argument: str) -> str:
        if self.min_length and len(argument) < self.min_length:
            raise BadArgument(f'The string "{argument}" is shorter than {self.min_length} character(s).')
        elif self.max_length and len(argument) > self.max_length:  # noqa: RET506
            raise BadArgument(f'The string "{argument}" is longer than {self.max_length} character(s).')

        return argument


class NarrowedChannelConverter(BaseChannelConverter):
    def __init__(self, channel_types: list[ChannelType | int]) -> None:
        self.channel_types = channel_types

    def _check(self, result: BaseChannel) -> bool:
        return result.type in self.channel_types


class HackyUnionConverter(Converter):
    def __init__(self, *converters: type[Converter]) -> None:
        self.converters = converters

    async def convert(self, ctx: BaseContext, arg: str) -> Any:
        for converter in self.converters:
            try:
                return await converter().convert(ctx, arg)
            except Exception:
                continue

        union_names = tuple(get_object_name(t).removesuffix("Converter") for t in self.converters)
        union_types_str = ", ".join(union_names[:-1]) + f", or {union_names[-1]}"
        raise BadArgument(f'Could not convert "{arg}" into {union_types_str}.')


class ChainConverter(Converter):
    def __init__(
        self,
        first_converter: Converter,
        second_converter: Callable,
        name_of_cmd: str,
    ) -> None:
        self.first_converter = first_converter
        self.second_converter = second_converter
        self.name_of_cmd = name_of_cmd

    async def convert(self, ctx: BaseContext, arg: str) -> Any:
        first = await self.first_converter.convert(ctx, arg)
        return await maybe_coroutine(self.second_converter, ctx, first)


class ChainNoArgConverter(NoArgumentConverter):
    def __init__(
        self,
        first_converter: NoArgumentConverter,
        second_converter: Callable,
        name_of_cmd: str,
    ) -> None:
        self.first_converter = first_converter
        self.second_converter = second_converter
        self.name_of_cmd = name_of_cmd

    async def convert(self, ctx: "HybridContext", _: Any) -> Any:
        first = await self.first_converter.convert(ctx, _)
        return await maybe_coroutine(self.second_converter, ctx, first)


def type_from_option(option_type: OptionType | int) -> Converter:
    if option_type == OptionType.STRING:
        return BasicConverter(str)
    elif option_type == OptionType.INTEGER:  # noqa: RET505
        return BasicConverter(int)
    elif option_type == OptionType.NUMBER:
        return BasicConverter(float)
    elif option_type == OptionType.BOOLEAN:
        return BoolConverter()
    elif option_type == OptionType.USER:
        return HackyUnionConverter(MemberConverter, UserConverter)
    elif option_type == OptionType.CHANNEL:
        return BaseChannelConverter()
    elif option_type == OptionType.ROLE:
        return RoleConverter()
    elif option_type == OptionType.MENTIONABLE:
        return HackyUnionConverter(MemberConverter, UserConverter, RoleConverter)
    elif option_type == OptionType.ATTACHMENT:
        return AttachmentConverter()
    raise NotImplementedError(f"Unknown option type: {option_type}")


@attrs.define(eq=False, order=False, hash=False, kw_only=True)
class HybridSlashCommand(SlashCommand):
    aliases: list[str] = attrs.field(repr=False, factory=list, metadata=no_export_meta)
    _dummy_base: bool = attrs.field(repr=False, default=False, metadata=no_export_meta)
    _silence_autocomplete_errors: bool = attrs.field(repr=False, default=False, metadata=no_export_meta)

    async def __call__(self, context: SlashContext, *args, **kwargs) -> None:
        new_ctx = context.client.hybrid.hybrid_context.from_slash_context(context)
        await super().__call__(new_ctx, *args, **kwargs)

    def group(
        self,
        name: str | None = None,
        description: str = "No Description Set",
        inherit_checks: bool = True,
        aliases: list[str] | None = None,
    ) -> "HybridSlashCommand":
        self._dummy_base = True
        return HybridSlashCommand(
            name=self.name,
            description=self.description,
            group_name=name,
            group_description=description,
            scopes=self.scopes,
            default_member_permissions=self.default_member_permissions,
            dm_permission=self.dm_permission,
            checks=self.checks.copy() if inherit_checks else [],
            aliases=aliases or [],
        )

    def subcommand(
        self,
        sub_cmd_name: Absent[LocalisedName | str] = MISSING,
        group_name: LocalisedName | str = None,
        sub_cmd_description: Absent[LocalisedDesc | str] = MISSING,
        group_description: Absent[LocalisedDesc | str] = MISSING,
        options: List[Union[SlashCommandOption, dict]] | None = None,
        nsfw: bool = False,
        inherit_checks: bool = True,
        aliases: list[str] | None = None,
        silence_autocomplete_errors: bool = True,
    ) -> Callable[..., "HybridSlashCommand"]:
        def wrapper(call: AsyncCallable) -> "HybridSlashCommand":
            nonlocal sub_cmd_name, sub_cmd_description

            if not asyncio.iscoroutinefunction(call):
                raise TypeError("Subcommand must be coroutine")

            if sub_cmd_description is MISSING:
                sub_cmd_description = call.__doc__ or "No Description Set"
            if sub_cmd_name is MISSING:
                sub_cmd_name = call.__name__

            self._dummy_base = True
            return HybridSlashCommand(
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
                checks=self.checks.copy() if inherit_checks else [],
                aliases=aliases or [],
                silence_autocomplete_errors=silence_autocomplete_errors,
            )

        return wrapper


@attrs.define(eq=False, order=False, hash=False, kw_only=True)
class _HybridToPrefixedCommand(PrefixedCommand):
    async def __call__(self, context: PrefixedContext, *args, **kwargs) -> None:
        new_ctx = context.client.hybrid.hybrid_context.from_prefixed_context(context)
        await super().__call__(new_ctx, *args, **kwargs)


def slash_to_prefixed(cmd: HybridSlashCommand) -> _HybridToPrefixedCommand:  # noqa: C901  there's nothing i can do
    prefixed_cmd = _HybridToPrefixedCommand(
        name=str(cmd.sub_cmd_name) if cmd.is_subcommand else str(cmd.name),
        aliases=list(_values_wrapper(cmd.sub_cmd_name.to_locale_dict()))
        if cmd.is_subcommand
        else list(_values_wrapper(cmd.name.to_locale_dict())),
        help=str(cmd.description),
        callback=cmd.callback,
        checks=cmd.checks,
        cooldown=cmd.cooldown,
        max_concurrency=cmd.max_concurrency,
        pre_run_callback=cmd.pre_run_callback,
        post_run_callback=cmd.post_run_callback,
        error_callback=cmd.error_callback,
    )
    if cmd.aliases:
        prefixed_cmd.aliases.extend(cmd.aliases)

    # copy over binding from slash command, if any
    # can't be done in init due to how _binding works
    prefixed_cmd._binding = cmd._binding

    if not cmd.dm_permission:
        prefixed_cmd.add_check(guild_only())

    if cmd.scopes != [GLOBAL_SCOPE]:
        prefixed_cmd.add_check(generate_scope_check(cmd.scopes))

    if cmd.default_member_permissions:
        prefixed_cmd.add_check(generate_permission_check(cmd.default_member_permissions))

    if not cmd.options:
        prefixed_cmd._inspect_signature = inspect.Signature()
        return prefixed_cmd

    fake_sig_parameters: list[inspect.Parameter] = []

    for option in cmd.options:
        if isinstance(option, dict):
            # makes my life easier
            option = SlashCommandOption(**option)

        if option.autocomplete and not cmd._silence_autocomplete_errors:
            # there isn't much we can do here
            raise ValueError("Autocomplete is unsupported in hybrid commands.")

        name = option.argument_name or str(option.name)
        annotation = inspect.Parameter.empty
        default = inspect.Parameter.empty
        kind = inspect.Parameter.POSITIONAL_ONLY if cmd._uses_arg else inspect.Parameter.POSITIONAL_OR_KEYWORD

        consume_rest: bool = False

        if slash_param := cmd.parameters.get(name):
            kind = slash_param.kind

            if kind == inspect.Parameter.KEYWORD_ONLY:  # work around prefixed cmd parsing
                kind = inspect.Parameter.POSITIONAL_OR_KEYWORD

            # here come the hacks - these allow ConsumeRest (the class) to be passed through
            if get_origin(slash_param.type) == Annotated:
                args = get_args(slash_param.type)
                # ComsumeRest[str] or Annotated[ConsumeRest[str], Converter] support
                # by all means, the second isn't allowed in prefixed commands, but we'll ignore that for converter support for slash cmds
                if args[1] is CONSUME_REST_MARKER or (
                    args[0] == Annotated and get_args(args[0])[1] is CONSUME_REST_MARKER
                ):
                    consume_rest = True

            if slash_param.converter:
                annotation = slash_param.converter
            if slash_param.default is not MISSING:
                default = slash_param.default

        if option.choices:
            option_anno = ChoicesConverter(option.choices)
        elif option.min_value is not None or option.max_value is not None:
            option_anno = RangeConverter(option.type, option.min_value, option.max_value)
        elif option.min_length is not None or option.max_length is not None:
            option_anno = StringLengthConverter(option.min_length, option.max_length)
        elif option.type == OptionType.CHANNEL and option.channel_types:
            option_anno = NarrowedChannelConverter(option.channel_types)
        else:
            option_anno = type_from_option(option.type)

        if annotation is inspect.Parameter.empty:
            annotation = option_anno
        elif isinstance(option_anno, NoArgumentConverter):
            annotation = ChainNoArgConverter(option_anno, annotation, name)
        else:
            annotation = ChainConverter(option_anno, annotation, name)

        if not option.required and default == inspect.Parameter.empty:
            default = None

        if consume_rest:
            annotation = ConsumeRest[annotation]

        actual_param = inspect.Parameter(
            name=name,
            kind=kind,
            default=default,
            annotation=annotation,
        )
        fake_sig_parameters.append(actual_param)

    prefixed_cmd._inspect_signature = inspect.Signature(parameters=fake_sig_parameters)
    return prefixed_cmd


def create_subcmd_func(group: bool = False) -> Callable:
    async def _subcommand_base(*args, **kwargs) -> None:
        if group:
            raise BadArgument("Cannot run this subcommand group without a valid subcommand.")
        raise BadArgument("Cannot run this command without a valid subcommand.")

    return _subcommand_base


def base_subcommand_generator(
    name: str, aliases: list[str], description: str, group: bool = False
) -> _HybridToPrefixedCommand:
    return _HybridToPrefixedCommand(
        callback=create_subcmd_func(group=group),
        name=name,
        aliases=aliases,
        help=description,
        ignore_extra=False,
        inspect_signature=inspect.Signature(None),  # type: ignore
    )


def hybrid_slash_command(
    name: Absent[str | LocalisedName] = MISSING,
    *,
    aliases: Optional[list[str]] = None,
    description: Absent[str | LocalisedDesc] = MISSING,
    scopes: Absent[list["Snowflake_Type"]] = MISSING,
    options: Optional[list[Union[SlashCommandOption, dict]]] = None,
    default_member_permissions: Optional["Permissions"] = None,
    dm_permission: bool = True,
    sub_cmd_name: str | LocalisedName = None,
    group_name: str | LocalisedName = None,
    sub_cmd_description: str | LocalisedDesc = "No Description Set",
    group_description: str | LocalisedDesc = "No Description Set",
    nsfw: bool = False,
    silence_autocomplete_errors: bool = False,
) -> Callable[[AsyncCallable], HybridSlashCommand]:
    """
    A decorator to declare a coroutine as a hybrid slash command.

    Hybrid commands are a slash command that can also function as a prefixed command.
    These use a HybridContext instead of an SlashContext, but otherwise are mostly identical to normal slash commands.

    Note that hybrid commands do not support autocompletes.
    They also only partially support attachments, allowing one attachment option for a command.

    !!! note
        While the base and group descriptions arent visible in the discord client, currently.
        We strongly advise defining them anyway, if you're using subcommands, as Discord has said they will be visible in
        one of the future ui updates.

    Args:
        name: 1-32 character name of the command, defaults to the name of the coroutine.
        aliases: Aliases for the prefixed command varient of the command. Has no effect on the slash command.
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
        silence_autocomplete_errors: Should autocomplete errors be silenced. Don't use this unless you know what you're doing.

    Returns:
        HybridSlashCommand Object

    """

    def wrapper(func: AsyncCallable) -> HybridSlashCommand:
        if not asyncio.iscoroutinefunction(func):
            raise ValueError("Commands must be coroutines")

        perm = default_member_permissions
        if hasattr(func, "default_member_permissions"):
            if perm:
                perm = perm | func.default_member_permissions
            else:
                perm = func.default_member_permissions

        _name = name
        if _name is MISSING:
            _name = func.__name__

        _description = description
        if _description is MISSING:
            _description = func.__doc__ or "No Description Set"

        cmd = HybridSlashCommand(
            name=_name,
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
            aliases=aliases or [],
            silence_autocomplete_errors=silence_autocomplete_errors,
        )

        return cmd

    return wrapper


def hybrid_slash_subcommand(
    base: str | LocalisedName,
    *,
    subcommand_group: Optional[str | LocalisedName] = None,
    name: Absent[str | LocalisedName] = MISSING,
    aliases: Optional[list[str]] = None,
    description: Absent[str | LocalisedDesc] = MISSING,
    base_description: Optional[str | LocalisedDesc] = None,
    base_desc: Optional[str | LocalisedDesc] = None,
    base_default_member_permissions: Optional["Permissions"] = None,
    base_dm_permission: bool = True,
    subcommand_group_description: Optional[str | LocalisedDesc] = None,
    sub_group_desc: Optional[str | LocalisedDesc] = None,
    scopes: List["Snowflake_Type"] | None = None,
    options: List[dict] | None = None,
    nsfw: bool = False,
    silence_autocomplete_errors: bool = False,
) -> Callable[[AsyncCallable], HybridSlashCommand]:
    """
    A decorator specifically tailored for creating hybrid slash subcommands.

    Args:
        base: The name of the base command
        subcommand_group: The name of the subcommand group, if any.
        name: The name of the subcommand, defaults to the name of the coroutine.
        aliases: Aliases for the prefixed command varient of the subcommand. Has no effect on the slash command.
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
        silence_autocomplete_errors: Should autocomplete errors be silenced. Don't use this unless you know what you're doing.

    Returns:
        A HybridSlashCommand object

    """

    def wrapper(func: AsyncCallable) -> HybridSlashCommand:
        if not asyncio.iscoroutinefunction(func):
            raise ValueError("Commands must be coroutines")

        _name = name
        if _name is MISSING:
            _name = func.__name__

        _description = description
        if _description is MISSING:
            _description = func.__doc__ or "No Description Set"

        cmd = HybridSlashCommand(
            name=base,
            description=(base_description or base_desc) or "No Description Set",
            group_name=subcommand_group,
            group_description=(subcommand_group_description or sub_group_desc) or "No Description Set",
            sub_cmd_name=_name,
            sub_cmd_description=_description,
            default_member_permissions=base_default_member_permissions,
            dm_permission=base_dm_permission,
            scopes=scopes or [GLOBAL_SCOPE],
            callback=func,
            options=options,
            nsfw=nsfw,
            aliases=aliases or [],
            silence_autocomplete_errors=silence_autocomplete_errors,
        )
        return cmd

    return wrapper
