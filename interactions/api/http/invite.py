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
        params_set = {"with_counts=true" if with_counts is True else None,
                      "with_expiration=false" if with_expiration is False else None,
                      f"guild_scheduled_event_id={guild_scheduled_event_id}" if guild_scheduled_event_id else None}
        final = "&".join([item for item in params_set if item is not None])

        # print(f"/invites/{invite_code}{'?' + final if final is not None else ''}")
        return await self._req.request(Route(
            "GET",
            f"/invites/{invite_code}{'?' + final if final is not None else ''}"
        ))

    async def delete_invite(self, invite_code: str) -> Invite:
        """
        Deletes an invite.
        :param invite_code: Invite code string
        :return: If successful, an Invite object is returned.
        """
        return await self._req.request(Route("DELETE", f"/invites/{invite_code}"))
