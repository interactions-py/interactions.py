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
    users: Dict[Union[str, int], User]
    members: Dict[Union[str, int], Member]
    roles: Dict[Union[str, int], Role]
    channels: Dict[Union[str, int], Channel]
    messages: Dict[Union[str, int], Message]


class InteractionData(DictSerializerMixin):
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
