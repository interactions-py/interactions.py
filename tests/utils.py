from interactions import Snowflake_Type, Client, Message
from interactions.models.internal.context import InteractionContext
from tests.consts import SAMPLE_MESSAGE_DATA
from interactions.ext.prefixed_commands import PrefixedContext

__all__ = ("generate_dummy_context",)


def generate_dummy_context(
    user_id: Snowflake_Type | None = None,
    channel_id: Snowflake_Type | None = None,
    guild_id: Snowflake_Type | None = None,
    message_id: Snowflake_Type | None = None,
    dm: bool = False,
    client: Client | None = None,
) -> InteractionContext:
    """Generates a dummy context for testing."""
    client = Client() if client is None else client

    if not dm and not guild_id:
        guild_id = "123456789012345670"
    elif dm:
        guild_id = None

    # channel = SAMPLE_CHANNEL_DATA(channel_id=channel_id, guild_id=guild_id)
    message = SAMPLE_MESSAGE_DATA(user_id=user_id, channel_id=channel_id, message_id=message_id, guild_id=guild_id)

    return PrefixedContext.from_message(client, Message.from_dict(message, client))
