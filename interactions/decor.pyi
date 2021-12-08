from typing import Any, Dict, List, Optional, Union

from .api.models.guild import Guild
from .enums import ApplicationCommandType
from .models.command import ApplicationCommand, Option

def command(
    *,
    type: Optional[Union[int, ApplicationCommandType]] = ApplicationCommandType.CHAT_INPUT,
    name: Optional[str] = None,
    description: Optional[str] = None,
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
    options: Optional[Union[Dict[str, Any], List[Dict[str, Any]], Option, List[Option]]] = None,
    default_permission: Optional[bool] = None,
    # permissions: Optional[
    #     Union[Dict[str, Any], List[Dict[str, Any]], Permission, List[Permission]]
    # ] = None,
) -> List[ApplicationCommand]: ...
def component(component: Union[Button, SelectMenu]) -> Component: ...
