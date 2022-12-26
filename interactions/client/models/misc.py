from typing import Dict, List, Optional

from ...api.models.channel import Channel
from ...api.models.member import Member
from ...api.models.message import Attachment, Message
from ...api.models.misc import Snowflake
from ...api.models.role import Role
from ...api.models.user import User
from ...utils.attrs_utils import DictSerializerMixin, convert_dict, convert_list, define, field
from ..enums import ApplicationCommandType, ComponentType, InteractionType
from ..models.command import Option
from .component import ActionRow

__all__ = ("InteractionResolvedData", "InteractionData", "Interaction")


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

    users: Dict[str, User] = field(converter=convert_dict(value_converter=User), factory=dict)
    members: Dict[str, Member] = field(converter=convert_dict(value_converter=Member), factory=dict)
    roles: Dict[str, Role] = field(converter=convert_dict(value_converter=Role), factory=dict)
    channels: Dict[str, Channel] = field(
        converter=convert_dict(value_converter=Channel), factory=dict
    )
    messages: Dict[str, Message] = field(
        converter=convert_dict(value_converter=Message), factory=dict
    )
    attachments: Dict[str, Attachment] = field(
        converter=convert_dict(value_converter=Attachment), factory=dict
    )

    def __attrs_post_init__(self):
        if self.members:
            # attrs has near zero way of filling this in automatically, so we have to
            for snowflake_id in self.members.keys():
                # members have User, user may not have Member. /shrug
                self.members[snowflake_id].user = self.users[snowflake_id]


@define()
class InteractionData(DictSerializerMixin):
    """
    A class object representing the data of an interaction.

    :ivar str id: The ID of the interaction data.
    :ivar str name: The name of the interaction.
    :ivar ApplicationCommandType type: The type of command from the interaction.
    :ivar Optional[InteractionResolvedData] resolved: The resolved version of the data.
    :ivar Optional[Option, List[Option]] options: The options of the interaction.
    :ivar Optional[str] custom_id: The custom ID of the interaction.
    :ivar Optional[ComponentType] component_type: The type of component from the interaction.
    :ivar Optional[List[str]] values: The values of the selected options in the interaction.
    :ivar Optional[str] target_id: The targeted ID of the interaction.
    :ivar Optional[List[ActionRow]] components: Array of Action Rows in modal.
    """

    id: Snowflake = field(converter=Snowflake, default=None)
    name: str = field(default=None)
    type: ApplicationCommandType = field(converter=ApplicationCommandType, default=None)
    resolved: Optional[InteractionResolvedData] = field(
        converter=InteractionResolvedData, default=None
    )
    options: Optional[List[Option]] = field(converter=convert_list(Option), default=None)
    custom_id: Optional[str] = field(default=None)
    component_type: Optional[ComponentType] = field(converter=ComponentType, default=None)
    values: Optional[List[str]] = field(default=None)
    target_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    components: Optional[List[ActionRow]] = field(converter=convert_list(ActionRow), default=None)


@define()
class Interaction(DictSerializerMixin):
    """
    A class object representing an interaction.

    :ivar str id: The ID of the interaction.
    :ivar str application_id: The application's ID of the interaction.
    :ivar InteractionType type: The type of interaction.
    :ivar Optional[InteractionData] data: The data of the interaction.
    :ivar Optional[str] guild_id: The guild ID of the interaction.
    :ivar Optional[str] channel_id: The channel ID of the interaction.
    :ivar Optional[Member] member: The member who invoked the interaction.
    :ivar Optional[User] user: The user who invoked the interaction.
    :ivar str token: The token of the interaction.
    :ivar int version: The version of the interaction as an autoincrement identifier.
    :ivar Optional[Message] message: The message of the interaction.
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

    def __attrs_post_init__(self):
        if self.member and self.guild_id:
            self.member._extras["guild_id"] = self.guild_id
