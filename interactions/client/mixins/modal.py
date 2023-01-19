import typing

if typing.TYPE_CHECKING:
    import interactions


class ModalMixin:
    client: "interactions.Client"
    """The client that created this context."""
    responded: bool
    """Whether this context has been responded to."""

    async def send_modal(self, modal: "interactions.Modal"):
        """Send a modal to the user."""
        if self.responded:
            raise RuntimeError("Cannot send modal after responding")
        ...
        self.responded = True