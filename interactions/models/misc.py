from typing import Dict, List, Optional, Union

from ..api.models.channel import Channel
from ..api.models.member import Member
from ..api.models.message import Message
from ..api.models.misc import DictSerializerMixin, Snowflake
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

    __slots__ = ("users", "members", "roles", "channels", "messages")


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

    id: Snowflake
    name: str
    type: ApplicationCommandType
    resolved: Optional[InteractionResolvedData]
    options: Optional[Union[Option, List[Option]]]
    custom_id: Optional[str]
    component_type: Optional[int]
    values: Optional[Union[SelectOption, List[SelectOption]]]
    target_id: Optional[Snowflake]

    __slots__ = (
        "_json",
        "id",
        "name",
        "type",
        "resolved",
        "options",
        "custom_id",
        "component_type",
        "values",
        "target_id",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = ApplicationCommandType(self.type) if self._json.get("type") else None
        self.resolved = (
            InteractionResolvedData(**self.resolved) if self._json.get("resolved") else None
        )
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.target_id = Snowflake(self.target_id) if self._json.get("target_id") else None


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

    id: Snowflake
    application_id: Snowflake
    type: InteractionType
    data: Optional[InteractionData]
    guild_id: Optional[Snowflake]
    channel_id: Optional[Snowflake]
    member: Optional[Member]
    user: Optional[User]
    token: str
    version: int
    message: Optional[Message]

    __slots__ = (
        "_json",
        "id",
        "application_id",
        "type",
        "data",
        "guild_id",
        "channel_id",
        "member",
        "user",
        "token",
        "version",
        "message",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = InteractionType(self.type)
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.application_id = (
            Snowflake(self.application_id) if self._json.get("application_id") else None
        )
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.channel_id = Snowflake(self.channel_id) if self._json.get("channel_id") else None
        self.member = Member(**self.member) if self._json.get("member") else None
        self.user = User(**self.user) if self._json.get("user") else None
