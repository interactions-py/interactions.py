from typing import Any, Dict, List, Optional, Union

from ..api.models.flags import Permissions
from ..api.models.guild import Guild
from .enums import ApplicationCommandType, Locale
from .models.command import ApplicationCommand, Option
from .models.component import Button, Component, SelectMenu

def command(
    *,
    type: Optional[Union[int, ApplicationCommandType]] = ApplicationCommandType.CHAT_INPUT,
    name: Optional[str] = None,
    description: Optional[str] = None,
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
    options: Optional[Union[Dict[str, Any], List[Dict[str, Any]], Option, List[Option]]] = None,
    name_localizations: Optional[Dict[Union[str, Locale], str]]  = None,
    description_localizations: Optional[Dict[Union[str, Locale], str]]  = None,
    default_member_permissions: Optional[Union[int, Permissions]] = None,
    dm_permission: Optional[bool] = None
) -> Union[List[dict], dict]: ...
def component(component: Union[Button, SelectMenu]) -> Component: ...
