from typing import TYPE_CHECKING, Optional

from ..route import Route, PAYLOAD_TYPE
from interactions.models.internal.protocols import CanRequest
from interactions.models.discord.snowflake import to_optional_snowflake, to_snowflake
from interactions.client.utils.serializer import dict_filter_none

if TYPE_CHECKING:
    from interactions.models.discord.snowflake import Snowflake_Type

__all__ = ("EntitlementRequests",)


class EntitlementRequests(CanRequest):
    async def get_entitlements(
        self,
        application_id: "Snowflake_Type",
        *,
        user_id: "Optional[Snowflake_Type]" = None,
        sku_ids: "Optional[list[Snowflake_Type]]" = None,
        before: "Optional[Snowflake_Type]" = None,
        after: "Optional[Snowflake_Type]" = None,
        limit: Optional[int] = 100,
        guild_id: "Optional[Snowflake_Type]" = None,
        exclude_ended: Optional[bool] = None,
    ) -> list[dict]:
        """
        Get an application's entitlements.

        Args:
            application_id: The ID of the application.
            user_id: The ID of the user to filter entitlements by.
            sku_ids: The IDs of the SKUs to filter entitlements by.
            before: Get entitlements before this ID.
            after: Get entitlements after this ID.
            limit: The maximum number of entitlements to return. Maximum is 100.
            guild_id: The ID of the guild to filter entitlements by.
            exclude_ended: Whether to exclude ended entitlements.

        Returns:
            A dictionary containing the application's entitlements.

        """
        params: PAYLOAD_TYPE = {
            "user_id": to_optional_snowflake(user_id),
            "sku_ids": [to_snowflake(sku_id) for sku_id in sku_ids] if sku_ids else None,
            "before": to_optional_snowflake(before),
            "after": to_optional_snowflake(after),
            "limit": limit,
            "guild_id": to_optional_snowflake(guild_id),
            "exclude_ended": exclude_ended,
        }
        params = dict_filter_none(params)

        return await self.request(
            Route("GET", "/applications/{application_id}/entitlements", application_id=application_id), params=params
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
