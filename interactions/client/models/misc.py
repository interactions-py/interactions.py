from typing import Any, Dict, List, Optional

from ...api.models.attrs_utils import DictSerializerMixin, convert_dict, convert_list, define, field
from ...api.models.channel import Channel
from ...api.models.member import Member
from ...api.models.message import Attachment, Message
from ...api.models.misc import Snowflake
from ...api.models.role import Role
from ...api.models.user import User
from ..enums import ApplicationCommandType, ComponentType, InteractionType, PermissionType
from ..models.command import Option


@define()
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

    users: Dict[str, User] = field(converter=convert_dict(value_converter=User))
    members: Dict[str, Member] = field(converter=convert_dict(value_converter=Member))
    roles: Dict[str, Role] = field(converter=convert_dict(value_converter=Role))
    channels: Dict[str, Channel] = field(converter=convert_dict(value_converter=Channel))
    messages: Dict[str, Message] = field(converter=convert_dict(value_converter=Message))
    attachments: Dict[str, Attachment] = field(converter=convert_dict(value_converter=Attachment))


@define()
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

    id: Snowflake = field(converter=Snowflake)
    name: str = field()
    type: ApplicationCommandType = field(converter=ApplicationCommandType)
    resolved: Optional[InteractionResolvedData] = field(
        converter=InteractionResolvedData, default=None
    )
    options: Optional[List[Option]] = field(converter=convert_list(Option), default=None)
    custom_id: Optional[str] = field(default=None)
    component_type: Optional[ComponentType] = field(
        converter=convert_list(ComponentType), default=None
    )
    values: Optional[List[str]] = field(default=None)
    target_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    components: Any = field(default=None)  # todo check this type

    def __attrs_post_init__(self, **kwargs):
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


@define()
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

    id: Snowflake = field(converter=Snowflake)
    application_id: Snowflake = field(converter=Snowflake)
    type: InteractionType = field(converter=InteractionType)
    data: Optional[InteractionData] = field(converter=InteractionData, default=None)
    guild_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    channel_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    member: Optional[Member] = field(converter=Member, default=None, add_client=True)
    user: Optional[User] = field(converter=User, default=None, add_client=True)
    token: str = field()
    version: int = field()
    message: Optional[Message] = field(converter=Message, default=None, add_client=True)


@define()
class Permission(DictSerializerMixin):
    """
    A class object representing the permission of an application command.

    The structure for a permission:

    .. code-block:: python

        interactions.Permission(
            id=1234567890,
            type=interactions.PermissionType.USER,
            permission=True,
        )

    :ivar int id: The ID of the permission.
    :ivar PermissionType type: The type of permission.
    :ivar bool permission: The permission state. ``True`` for allow, ``False`` for disallow.
    """

    id: int = field()
    type: PermissionType = field(converter=PermissionType)
    permission: bool = field()
