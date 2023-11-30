from typing import Any, TYPE_CHECKING, List

import discord_typings

from interactions.client.const import MISSING, Absent
from ..route import Route

__all__ = ("ScheduledEventsRequests",)


if TYPE_CHECKING:
    from interactions.models.discord.snowflake import Snowflake_Type


class ScheduledEventsRequests:
    request: Any

    async def list_schedules_events(
        self, guild_id: "Snowflake_Type", with_user_count: bool = False
    ) -> List[discord_typings.GuildScheduledEventData]:
        """
        Get the scheduled events for a guild.

        Args:
            guild_id: The guild to get scheduled events from
            with_user_count: Whether to include the user count in the response
        Returns:
            List of Scheduled Events or None

        """
        return await self.request(
            Route(
                "GET",
                "/guilds/{guild_id}/scheduled-events?with_user_count={with_user_count}",
                guild_id=guild_id,
                with_user_count=with_user_count,
            )
        )

    async def get_scheduled_event(
        self,
        guild_id: "Snowflake_Type",
        scheduled_event_id: "Snowflake_Type",
        with_user_count: bool = False,
    ) -> discord_typings.GuildScheduledEventData:
        """
        Get a scheduled event for a guild.

        Args:
            guild_id: The guild to get scheduled event from
            scheduled_event_id: The target scheduled event to fetch
            with_user_count: Whether to include the user count in the response

        Returns:
            Scheduled Event or None

        """
        return await self.request(
            Route(
                "GET",
                "/guilds/{guild_id}/scheduled-events/{scheduled_event_id}?with_user_count={with_user_count}",
                guild_id=guild_id,
                scheduled_event_id=scheduled_event_id,
                with_user_count=with_user_count,
            ),
        )

    async def create_scheduled_event(
        self,
        guild_id: "Snowflake_Type",
        payload: dict,
        reason: Absent[str] = MISSING,
    ) -> discord_typings.GuildScheduledEventData:
        """
        Create a scheduled event for a guild.

        Args:
            guild_id: The guild to create scheduled event from
            payload: The scheduled event payload
            reason: The reason to be displayed in audit logs

        Returns:
            Scheduled Event or None

        """
        return await self.request(
            Route("POST", "/guilds/{guild_id}/scheduled-events", guild_id=guild_id), payload=payload, reason=reason
        )

    async def modify_scheduled_event(
        self,
        guild_id: "Snowflake_Type",
        scheduled_event_id: "Snowflake_Type",
        payload: dict,
        reason: Absent[str] = MISSING,
    ) -> discord_typings.GuildScheduledEventData:
        """
        Modify a scheduled event for a guild.

        Args:
            guild_id: The guild to modify scheduled event from
            scheduled_event_id: The scheduled event to modify
            payload: The payload to modify the scheduled event with
            reason: The reason to be displayed in audit logs

        Returns:
            Scheduled Event or None

        """
        return await self.request(
            Route(
                "PATCH",
                "/guilds/{guild_id}/scheduled-events/{scheduled_event_id}",
                guild_id=guild_id,
                scheduled_event_id=scheduled_event_id,
            ),
            payload=payload,
            reason=reason,
        )

    async def delete_scheduled_event(
        self,
        guild_id: "Snowflake_Type",
        scheduled_event_id: "Snowflake_Type",
        reason: Absent[str] = MISSING,
    ) -> None:
        """
        Delete a scheduled event for a guild.

        Args:
            guild_id: The guild to delete scheduled event from
            scheduled_event_id: The scheduled event to delete
            reason: The reason to be displayed in audit logs

        """
        return await self.request(
            Route(
                "DELETE",
                "/guilds/{guild_id}/scheduled-events/{scheduled_event_id}",
                guild_id=guild_id,
                scheduled_event_id=scheduled_event_id,
            ),
            reason=reason,
        )

    async def get_scheduled_event_users(
        self,
        guild_id: "Snowflake_Type",
        scheduled_event_id: "Snowflake_Type",
        limit: int = 100,
        with_member: bool = False,
        before: "Snowflake_Type" = MISSING,
        after: "Snowflake_Type" = MISSING,
    ) -> List[discord_typings.GuildScheduledEventUserData]:
        """
        Get the users for a scheduled event.

        Args:
            guild_id: The guild to get scheduled event users from
            scheduled_event_id: The scheduled event to get users from
            limit: how many users to receive from the event
            with_member: include guild member data if it exists
            before: consider only users before given user id
            after: consider only users after given user id

        Returns:
            List of Scheduled Event Users or None

        """
        params = {"limit": limit, "with_member": with_member, "before": before, "after": after}
        return await self.request(
            Route(
                "GET",
                "/guilds/{guild_id}/scheduled-events/{scheduled_event_id}/users",
                guild_id=guild_id,
                scheduled_event_id=scheduled_event_id,
            ),
            params=params,
        )
