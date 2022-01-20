from typing import Any, Dict, List, Optional, Union

from interactions.models.component import Button, SelectMenu

from .api.models.guild import Guild
from .enums import ApplicationCommandType
from .models.command import ApplicationCommand, Option
from .models.component import Component


def command(
    *,
    type: Optional[Union[int, ApplicationCommandType]] = ApplicationCommandType.CHAT_INPUT,
    name: Optional[str] = None,
    description: Optional[str] = None,
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
    options: Optional[Union[Dict[str, Any], List[Dict[str, Any]], Option, List[Option]]] = None,
    default_permission: Optional[bool] = None,
) -> List[ApplicationCommand]:
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

    _description: str = "" if description is None else description
    _options: list = []

    if options:
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

    _default_permission: bool = True if default_permission is None else default_permission
    _scope: list = []

    payloads: list = []

    if scope:
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
                default_permission=_default_permission,
            )
            payloads.append(payload._json)
    else:
        payload: ApplicationCommand = ApplicationCommand(
            type=_type,
            name=name,
            description=_description,
            options=_options,
            default_permission=_default_permission,
        )
        payloads.append(payload._json)

    return payloads


def component(component: Union[Button, SelectMenu]) -> Component:
    """
    A wrapper designed to interpret the client-facing API for
    how a component is to be declared and called back.

    :return: A component.
    :rtype: Component
    """
    return Component(**component._json)
