import typing

from interactions.models.discord.snowflake import Snowflake

if typing.TYPE_CHECKING:
    import interactions

__all__ = ("ModalMixin",)


class ModalMixin:
    client: "interactions.client.client.Client"
    """The client that created this context."""
    responded: bool
    """Whether this context has been responded to."""
    id: Snowflake
    """The interaction ID."""
    token: str
    """The interaction token."""

    async def send_modal(self, modal: "interactions.Modal") -> "dict | interactions.Modal":
        """Send a modal to the user."""
        if self.responded:
            raise RuntimeError("Cannot send modal after responding")
        payload = modal if isinstance(modal, dict) else modal.to_dict()

        await self.client.http.post_initial_response(payload, self.id, self.token)

        self.responded = True
        return modal
