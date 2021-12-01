from typing import Dict, List, Optional, Union

from ..api.models.channel import Channel
from ..api.models.member import Member
from ..api.models.message import Message
from ..api.models.misc import DictSerializerMixin
from ..api.models.role import Role
from ..api.models.user import User
from ..enums import ApplicationCommandType, InteractionType
from ..models.command import Option
from ..models.component import SelectOption


class InteractionResolvedData:
    """
    A class representing the resolved information of an interaction data.

    :ivar Dict[Union[str, int], User] users: The resolved users data.
    :ivar Dict[Union[str, int], Member] members: The resolved members data.
    :ivar Dict[Union[str, int], Role] roles: The resolved roles data.
    :ivar Dict[Union[str, int], Channel] channels: The resolved channels data.
    :ivar Dict[Union[str, int], Message] messages: The resolved messages data.
    """

    users: Dict[Union[str, int], User]
    members: Dict[Union[str, int], Member]
    roles: Dict[Union[str, int], Role]
    channels: Dict[Union[str, int], Channel]
    messages: Dict[Union[str, int], Message]


class InteractionData(DictSerializerMixin):
    """
    A class object representing the data of an interaction.

    :ivar str id: The ID of the interaction data.
    :ivar str name: The name of the interaction.
    :ivar ApplicationCommandType type: The type of command from the interaction.
    :ivar Optional[InteractionResolvedData] resolved?: The resolved version of the data.
    :ivar Optional[Union[Option, List[Option]]] options?: The options of the interaction.
    :ivar Optional[str] custom_id?: The custom ID of the interaction.
    :ivar Optional[int] component_type?: The type of component from the interaction.
    :ivar Optional[Union[SelectOption, List[SelectOption]]] values?: The values of the selected options in the interaction.
    :ivar Optional[str] target_id?: The targeted ID of the interaction.
    """

    id: str
    name: str
    type: ApplicationCommandType
    resolved: Optional[InteractionResolvedData]
    options: Optional[Union[Option, List[Option]]]
    custom_id: Optional[str]
    component_type: Optional[int]
    values: Optional[Union[SelectOption, List[SelectOption]]]
    target_id: Optional[str]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


class Interaction(DictSerializerMixin):
    """
    A class object representing an interaction.

    :ivar str id: The ID of the interaction.
    :ivar str application_id: The application's ID of the interaction.
    :ivar InteractionType type: The type of interaction.
    :ivar Optional[InteractionData] data?: The data of the interaction.
    :ivar Optional[str] guild_id?: The guild ID of the interaction.
    :ivar Optional[str] channel_id?: The channel ID of the interaction.
    :ivar Optional[Member] member?: The member who invoked the interaction.
    :ivar Optional[User] user?: The user who invoked the interaction.
    :ivar str token: The token of the interaction.
    :ivar version: The version of the interaction as an autoincrement identifier.
    :ivar Optional[Message] message?: The message of the interaction.
    """

    id: str
    application_id: str
    type: InteractionType
    data: Optional[InteractionData]
    guild_id: Optional[str]
    channel_id: Optional[str]
    member: Optional[Member]
    user: Optional[User]
    token: str
    version: int = 1
    message: Optional[Message]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
