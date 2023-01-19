import typing
from typing import Protocol, Any, TYPE_CHECKING

from interactions.api.http.route import Route
from interactions.client.const import T_co
from interactions.models.discord.file import UPLOADABLE_TYPE

if TYPE_CHECKING:
    from interactions.models.internal.context import BaseContext

__all__ = ("Converter",)


@typing.runtime_checkable
class Converter(Protocol[T_co]):
    """A protocol representing a class used to convert an argument."""

    async def convert(self, ctx: "BaseContext", argument: Any) -> T_co:
        """
        The function that converts an argument to the appropriate type.

        This should be overridden by subclasses for their conversion logic.

        Args:
            ctx: The context to use for the conversion.
            argument: The argument to be converted.

        Returns:
            Any: The converted argument.
        """
        raise NotImplementedError("Derived classes need to implement this.")


class CanRequest(Protocol[T_co]):
    async def request(
        self,
        route: Route,
        payload: list | dict | None = None,
        files: list[UPLOADABLE_TYPE] | None = None,
        reason: str | None = None,
        params: dict | None = None,
        **kwargs: dict,
    ) -> str | dict[str, Any] | None:
        raise NotImplementedError("Derived classes need to implement this.")
