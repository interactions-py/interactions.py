from typing import Any, Dict, List, Optional, Union

from ..api.models.flags import Permissions
from ..api.models.guild import Guild
from ..utils.missing import MISSING
from .enums import ApplicationCommandType, Locale
from .models.command import ApplicationCommand, Option
from .models.component import Button, Component, SelectMenu

__all__ = ("command", "component")


def command(
    *,
    type: Optional[Union[int, ApplicationCommandType]] = ApplicationCommandType.CHAT_INPUT,
    name: Optional[str] = MISSING,
    description: Optional[str] = MISSING,
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = MISSING,
    options: Optional[Union[Dict[str, Any], List[Dict[str, Any]], Option, List[Option]]] = MISSING,
    name_localizations: Optional[Dict[Union[str, Locale], str]] = MISSING,
    description_localizations: Optional[Dict[Union[str, Locale], str]] = MISSING,
    default_member_permissions: Optional[Union[int, Permissions]] = MISSING,
    dm_permission: Optional[bool] = MISSING
) -> Union[List[dict], dict]:  # sourcery skip: low-code-quality
    """
    A wrapper designed to interpret the client-facing API for
    how a command is to be created and used.

    :return: A list of command payloads.
    :rtype: List[ApplicationCommand]
    """
    _type: int = 0
    if isinstance(type, ApplicationCommandType):
        _type: int = type.value
    else:
        _type: int = ApplicationCommandType(type).value

    _description: str = "" if description is MISSING else description
    _options: list = []

    _name_localizations = (
        {}
        if name_localizations is MISSING
        else {k.value if isinstance(k, Locale) else k: v for k, v in name_localizations.items()}
    )
    _description_localizations = (
        {}
        if description_localizations is MISSING
        else {
            k.value if isinstance(k, Locale) else k: v for k, v in description_localizations.items()
        }
    )

    if options is not MISSING:
        if all(isinstance(option, Option) for option in options):
            _options = [option._json for option in options]
        elif all(
            isinstance(option, dict) and all(isinstance(value, str) for value in option)
            for option in options
        ):
            _options = list(options)
        elif isinstance(options, Option):
            _options = [options._json]
        else:
            _options = [options]

    _scope: list = []

    _default_member_permissions: str = (
        str(Permissions.USE_APPLICATION_COMMANDS.value)
        if default_member_permissions is MISSING
        else str(
            (
                default_member_permissions.value
                if isinstance(default_member_permissions, Permissions)
                else default_member_permissions
            )
        )
    )
    _dm_permission: bool = True if dm_permission is MISSING else dm_permission

    payloads: list = []

    if scope is not MISSING:
        if isinstance(scope, list):
            if all(isinstance(guild, Guild) for guild in scope):
                [_scope.append(guild.id) for guild in scope]
            elif all(isinstance(guild, int) for guild in scope):
                [_scope.append(guild) for guild in scope]
        else:
            _scope.append(scope)

    if _scope:
        for guild in _scope:
            payload: ApplicationCommand = ApplicationCommand(
                type=_type,
                guild_id=guild,
                name=name,
                description=_description,
                options=_options,
                name_localizations=_name_localizations,
                description_localizations=_description_localizations,
                default_member_permissions=_default_member_permissions,
                dm_permission=_dm_permission,
            )
            payloads.append(payload._json)
    else:
        payload: ApplicationCommand = ApplicationCommand(
            type=_type,
            name=name,
            description=_description,
            options=_options,
            name_localizations=_name_localizations,
            description_localizations=_description_localizations,
            default_member_permissions=_default_member_permissions,
            dm_permission=_dm_permission,
        )
        return payload._json

    return payloads


def component(component: Union[Button, SelectMenu]) -> Component:
    """
    A wrapper designed to interpret the client-facing API for
    how a component is to be declared and called back.

    :return: A component.
    :rtype: Component
    """
    return Component(**component._json)
