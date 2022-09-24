from typing import List

from ...api.cache import Cache
from .request import _Request
from .route import Route

__all__ = ("ScheduledEventRequest",)


class ScheduledEventRequest:

    _req: _Request
    cache: Cache

    def __init__(self) -> None:
        pass

    async def create_scheduled_event(self, guild_id: int, payload: dict) -> dict:
        """
        Creates a scheduled event.

        :param guild_id: Guild ID snowflake.
        :param payload: The dictionary containing the parameters and values to edit the associated event.
        :return: A dictionary containing the new guild scheduled event object on success.
        """
        valid_keys = (
            "channel_id",
            "name",
            "privacy_level",
            "scheduled_start_time",
            "scheduled_end_time",
            "entity_metadata",
            "description",
            "entity_type",
        )
        data = {k: v for k, v in payload.items() if k in valid_keys}

        return await self._req.request(
            Route("POST", "/guilds/{guild_id}/scheduled-events", guild_id=guild_id), json=data
        )

    async def get_scheduled_event(
        self, guild_id: int, guild_scheduled_event_id: int, with_user_count: bool
    ) -> dict:
        """
        Gets a guild scheduled event.

        :param guild_id: Guild ID snowflake.
        :param guild_scheduled_event_id: Guild Scheduled Event ID snowflake.
        :param with_user_count: Whether the number of users subscribed to the events is returned.
        :return: A dictionary containing the guild scheduled event object on success.
        """

        return await self._req.request(
            Route(
                "GET",
                "/guilds/{guild_id}/scheduled-events/{event_id}",
                guild_id=guild_id,
                event_id=guild_scheduled_event_id,
            ),
            params={"with_user_count": str(with_user_count).lower()},
        )

    async def get_scheduled_events(self, guild_id: int, with_user_count: bool) -> List[dict]:
        """
        Gets all guild scheduled events in a guild.

        :param guild_id: Guild ID snowflake.
        :param with_user_count: Whether the number of users subscribed to the associated event is returned.
        :return: A List of a dictionary containing the guild scheduled event objects on success.
        """
        return await self._req.request(
            Route("GET", "/guilds/{guild_id}/scheduled-events", guild_id=guild_id),
            params={"with_user_count": str(with_user_count).lower()},
        )

    async def modify_scheduled_event(
        self, guild_id: int, guild_scheduled_event_id: int, payload: dict
    ) -> dict:
        """
        Modifies a scheduled event.

        :param guild_id: Guild ID snowflake.
        :param guild_scheduled_event_id: Guild Scheduled Event ID snowflake.
        :param payload: The dictionary containing the parameters and values to edit the associated event.
        :return: A dictionary containing the updated guild scheduled event object on success.
        """
        valid_keys = (
            "channel_id",
            "name",
            "privacy_level",
            "scheduled_start_time",
            "scheduled_end_time",
            "entity_metadata",
            "description",
            "entity_type",
        )
        data = {k: v for k, v in payload.items() if k in valid_keys}
        return await self._req.request(
            Route(
                "PATCH",
                "/guilds/{guild_id}/scheduled-events/{event_id}",
                guild_id=guild_id,
                event_id=guild_scheduled_event_id,
            ),
            json=data,
        )

    async def delete_scheduled_event(self, guild_id: int, guild_scheduled_event_id: int) -> None:
        """
        Deletes a guild scheduled event.

        :param guild_id: Guild ID snowflake.
        :param guild_scheduled_event_id: Guild Scheduled Event ID snowflake.
        :return: Nothing on success.
        """

        return await self._req.request(
            Route(
                "DELETE",
                "/guilds/{guild_id}/scheduled-events/{event_id}",
                guild_id=guild_id,
                event_id=guild_scheduled_event_id,
            )
        )

    async def get_scheduled_event_users(
        self,
        guild_id: int,
        guild_scheduled_event_id: int,
        limit: int = 100,
        with_member: bool = False,
        before: int = None,
        after: int = None,
    ) -> dict:
        """
        Get the registered users of a scheduled event.

        :param guild_id: Guild ID snowflake.
        :param guild_scheduled_event_id: Guild Scheduled Event snowflake.
        :param limit: Limit of how many users to pull from the event. Defaults to 100.
        :param with_member: Include guild member data if it exists. Defaults to False.
        :param before: Considers only users before given user ID snowflake. Defaults to None.
        :param after: Considers only users after given user ID snowflake. Defaults to None.
        :return: Returns a list of guild scheduled event user objects on success.
        """
        params = {
            "limit": limit,
            "with_member": with_member,
        }
        if before:
            params["before"] = before
        if after:
            params["after"] = after

        return await self._req.request(
            Route(
                "GET",
                "/guilds/{guild_id}/scheduled-events/{event_id}/users",
                guild_id=guild_id,
                event_id=guild_scheduled_event_id,
            ),
            params=params,
        )
