from typing import TYPE_CHECKING

from ..route import Route
from interactions.models.internal.protocols import CanRequest

if TYPE_CHECKING:
    from interactions.models.discord.snowflake import Snowflake_Type

__all__ = ("EntitlementRequests",)


class EntitlementRequests(CanRequest):
    async def get_entitlements(self, application_id: "Snowflake_Type") -> list[dict]:
        """
        Get an application's entitlements.

        Args:
            application_id: The ID of the application.

        Returns:
            A dictionary containing the application's entitlements.
        """
        return await self.request(
            Route("GET", "/applications/{application_id}/entitlements", application_id=application_id)
        )

    async def create_test_entitlement(self, payload: dict, application_id: "Snowflake_Type") -> dict:
        """
        Create a test entitlement for an application.

        Args:
            payload: The entitlement's data.
            application_id: The ID of the application.

        Returns:
            A dictionary containing the test entitlement.
        """
        return await self.request(
            Route("POST", "/applications/{application_id}/entitlements", application_id=application_id), payload=payload
        )

    async def delete_test_entitlement(self, application_id: "Snowflake_Type", entitlement_id: "Snowflake_Type") -> None:
        """
        Delete a test entitlement for an application.

        Args:
            application_id: The ID of the application.
            entitlement_id: The ID of the entitlement.
        """
        await self.request(
            Route(
                "DELETE",
                "/applications/{application_id}/entitlements/{entitlement_id}",
                application_id=application_id,
                entitlement_id=entitlement_id,
            )
        )
