from typing import Union, Optional
from .request import _Request
from .route import Route
from ..models.guild import Invite
from ...api.cache import Cache


class InviteRequest:
    _req = _Request
    cache: Cache

    def __init__(self) -> None:
        pass

    async def get_invite(
            self,
            invite_code: str,
            with_counts: bool = None,
            with_expiration: bool = None,
            guild_scheduled_event_id: int = None
    ) -> dict:
        """
        Gets an invite using its code.

        :param invite_code: A string representing the invite code.
        :param with_counts: Whether approximate_member_count and approximate_presence_count are returned.
        :param with_expiration: Whether the invite's expiration is returned.
        :param guild_scheduled_event_id: A guild scheduled event's ID.
        """
        params_set = {"with_counts=true" if with_counts is True else None,
                      "with_expiration=false" if with_expiration is False else None,
                      f"guild_scheduled_event_id={guild_scheduled_event_id}" if guild_scheduled_event_id else None}
        final = "&".join([item for item in params_set if item is not None])

        return await self._req.request(Route(
            "GET",
            f"/invites/{invite_code}{'?' + final if final is not None else ''}"
        ))

    async def delete_invite(self, invite_code: str, reason: Optional[str] = None) -> dict:
        """
        Delete an invite.

        :param invite_code: The code of the invite to delete
        :param reason: Reason to show in the audit log, if any.
        :return: The deleted invite object
        """
        return await self._req.request(Route("DELETE", f"/invites/{invite_code}"), reason=reason)
