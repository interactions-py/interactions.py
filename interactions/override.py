# Normal libraries
from typing import Union, Any, Optional

# 3rd-party libraries
from discord import Message as _Message
from discord.channel import DMChannel, GroupChannel, TextChannel
from discord.state import ConnectionState
# from discord.types.message import Message as MessagePayload

class Message(_Message):
    """
    Object representing the base of Rapptz's message object.

    .. note:

        This extends off of `discord.Message <https://github.com/Rapptz/discord.py/blob/master/discord/message.py#L487>`_ from discord.py.
    """
    __slots__ = tuple(list(_Message.__slots__) + ["components"])
    components: Any

    def __init__(
        self,
        *,
        state: ConnectionState,
        channel: Union[TextChannel, DMChannel, GroupChannel],
        data: Any
    ) -> None:
        """
        Instantiates the BaseMessage class.

        :param state: The current asynchronous state of connection.
        :type state: discord.state.ConnectionState
        :param channel: The channel the message came from.
        :type channel: typing.Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel]
        :param data: The data to pass through the message.
        :type data: typing.Any
        :return: None
        """
        super().__init__(
            state=state,
            channel=channel,
            data=data
        )
        self.components = data["components"]

    def get_component(
        self,
        custom_id: int
    ) -> Optional[dict]:
        """
        Retrieves a component given from the message.

        :param custom_id: The unique ID/identifier of the component.
        :type custom_id: int
        :return: typing.Optional[dict]
        """
        components: list = [[component for component in row["components"]] for row in self.components]
        for component in components:
            if (
                "custom_id" in component
                and component["custom_id"] == custom_id
            ):
                return component

def new_override(
    cls,
    *args,
    **kwargs
):
    return object.__new__(Message) if isinstance(cls, _Message) else object.__new__(cls)

_Message.__new__ = new_override