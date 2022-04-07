from typing import Dict, List, Optional

from ..api.models.channel import Channel
from ..api.models.member import Member
from ..api.models.message import Attachment, Message
from ..api.models.misc import DictSerializerMixin, Snowflake
from ..api.models.role import Role
from ..api.models.user import User
from ..enums import ApplicationCommandType, ComponentType, InteractionType
from ..models.command import Option


class InteractionResolvedData(DictSerializerMixin):
    """
    A class representing the resolved information of an interaction data.

    :ivar Dict[str, User] users: The resolved users data.
    :ivar Dict[str, Member] members: The resolved members data.
    :ivar Dict[str, Role] roles: The resolved roles data.
    :ivar Dict[str, Channel] channels: The resolved channels data.
    :ivar Dict[str, Message] messages: The resolved messages data.
    :ivar Dict[str, Attachment] attachments: The resolved attachments data.
    """

    __slots__ = ("_json", "users", "members", "roles", "channels", "messages", "attachments")
    users: Dict[str, User]
    members: Dict[str, Member]
    roles: Dict[str, Role]
    channels: Dict[str, Channel]
    messages: Dict[str, Message]
    attachments: Dict[str, Attachment]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self._json.get("users"):
            [
                self.users.update({user: User(**self.users[user])})
                for user in self._json.get("users")
            ]
        else:
            self.users = {}
        if self._json.get("members"):
            [
                self.members.update(
                    {member: Member(**self.members[member], user=self.users[member])}
                )
                for member in self._json.get("members")
            ]  # members have User, user may not have Member. /shrug
        else:
            self.members = {}
        if self._json.get("roles"):
            [
                self.roles.update({role: Role(**self.roles[role])})
                for role in self._json.get("roles")
            ]
        else:
            self.roles = {}
        if self._json.get("channels"):
            [
                self.channels.update({channel: Channel(**self.channels[channel])})
                for channel in self._json.get("channels")
            ]
        else:
            self.channels = {}
        if self._json.get("messages"):
            [
                self.messages.update({message: Message(**self.messages[message])})
                for message in self._json.get("messages")
            ]
        else:
            self.messages = {}
        if self._json.get("attachments"):
            [
                self.attachments.update({attachment: Attachment(**self.attachments[attachment])})
                for attachment in self._json.get("attachments")
            ]
        else:
            self.attachments = {}


class InteractionData(DictSerializerMixin):
    """
    A class object representing the data of an interaction.

    :ivar str id: The ID of the interaction data.
    :ivar str name: The name of the interaction.
    :ivar ApplicationCommandType type: The type of command from the interaction.
    :ivar Optional[InteractionResolvedData] resolved?: The resolved version of the data.
    :ivar Optional[Option, List[Option]] options?: The options of the interaction.
    :ivar Optional[str] custom_id?: The custom ID of the interaction.
    :ivar Optional[ComponentType] component_type?: The type of component from the interaction.
    :ivar Optional[List[str]] values?: The values of the selected options in the interaction.
    :ivar Optional[str] target_id?: The targeted ID of the interaction.
    """

    id: Snowflake
    name: str
    type: ApplicationCommandType
    resolved: Optional[InteractionResolvedData]
    options: Optional[List[Option]]
    custom_id: Optional[str]
    component_type: Optional[ComponentType]
    values: Optional[List[str]]
    target_id: Optional[Snowflake]

    __slots__ = (
        "_json",
        "id",
        "name",
        "type",
        "resolved",
        "options",
        "custom_id",
        "components",
        "component_type",
        "values",
        "target_id",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self._json.get("type"):
            self.type = ApplicationCommandType(self.type)
            self._json.update({"type": self.type.value})
        else:
            self.type = 0
        self.resolved = (
            InteractionResolvedData(**self.resolved) if self._json.get("resolved") else None
        )
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.target_id = Snowflake(self.target_id) if self._json.get("target_id") else None
        self.options = (
            [Option(**option) for option in self.options] if self._json.get("options") else None
        )
        self.values = self.values if self._json.get("values") else None
        if self._json.get("component_type"):
            self.component_type = ComponentType(self.component_type)
            self._json.update({"component_type": self.component_type.value})


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
        self.data = InteractionData(**self.data) if self._json.get("data") else None
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.channel_id = Snowflake(self.channel_id) if self._json.get("channel_id") else None
        self.member = Member(**self.member) if self._json.get("member") else None
        self.user = User(**self.user) if self._json.get("user") else None
