import interactions.client

from .api.http import HTTPClient
from .api.models.misc import DictSerializerMixin


class Context(DictSerializerMixin):
    r"""
    The base class of \"context\" for dispatched event data
    from the gateway.

    :ivar interactions.api.models.message.Message message: The message data model.
    :ivar interactions.api.models.member.Member author: The member data model.
    :ivar interactions.api.models.user.User user: The user data model.
    :ivar interactions.api.models.channel.Channel channel: The channel data model.
    :ivar interactions.api.models.guild.Guild guild: The guild data model.
    :ivar \*args: Multiple arguments of the context.
    :ivar \**kwargs: Keyword-only arguments of the context.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


class InteractionContext(Context):
    """
    This is a derivation of the base Context class designed specifically for
    interaction data.

    :ivar str id: The ID of the interaction.
    :ivar str application_id: The application ID of the interaction.
    :ivar typing.Union[str, int, interactions.enums.InteractionType] type: The type of interaction.
    :ivar interactions.models.misc.InteractionData data: The application command data.
    :ivar str guild_id: The guild ID the interaction falls under.
    :ivar str channel_id: The channel ID the interaction was instantiated from.
    :ivar str token: The token of the interaction response.
    :ivar int=1 version: The version of interaction creation. Always defaults to ``1``.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    async def send(self, content: str) -> None:
        """
        A **very** primitive form of the send model to get the uttermost
        basic implementation of command responses up and running.

        ok he kinda work now
        """
        payload: dict = {
            "type": 4,
            "data": {
                "content": content,
                "tts": False,
                "embeds": [],
                "allowed_mentions": {},
                "components": [],
            },
        }

        req = await HTTPClient(interactions.client.cache.token)._create_interaction_response(
            token=self.token, application_id=int(self.id), data=payload
        )
        return req


class ComponentContext(InteractionContext):
    """
    This is a derivation of the base Context class designed specifically for
    component data.

    :ivar str custom_id: The customized ID for the component to call.
    :ivar typing.Union[str, int, interactions.enums.ComponentType] type: The type of component.
    :ivar list values: The curated list of values under the component. This will be ``None`` if the type is not ``SELECT_MENU``.
    :ivar bool origin: Whether this is the origin of the component.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
