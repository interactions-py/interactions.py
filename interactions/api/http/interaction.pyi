from typing import List, Optional, Union

from ..models import Snowflake
from ...api.cache import Cache
from .request import _Request


class InteractionRequest:

    _req: _Request
    cache: Cache

    def __init__(self) -> None: ...

    async def get_application_commands(
        self, application_id: Union[int, Snowflake], guild_id: Optional[int] = None,
        with_localizations: Optional[bool] = None
    ) -> List[dict]: ...
    async def create_application_command(
        self, application_id: Union[int, Snowflake], data: dict, guild_id: Optional[int] = None
    ) -> dict: ...
    async def overwrite_application_command(
        self, application_id: int, data: List[dict], guild_id: Optional[int] = None
    ) -> List[dict]: ...
    async def edit_application_command(
        self,
        application_id: Union[int, Snowflake],
        data: dict,
        command_id: Union[int, Snowflake],
        guild_id: Optional[int] = None,
    ) -> dict: ...
    async def delete_application_command(
        self, application_id: Union[int, Snowflake], command_id: int, guild_id: Optional[int] = None
    ) -> None: ...
    async def edit_application_command_permissions(
        self, application_id: int, guild_id: int, command_id: int, data: List[dict]
    ) -> dict: ...
    async def get_application_command_permissions(
        self, application_id: int, guild_id: int, command_id: int
    ) -> dict: ...
    async def get_all_application_command_permissions(
        self, application_id: int, guild_id: int
    ) -> List[dict]: ...
    async def create_interaction_response(
        self, token: str, application_id: int, data: dict
    ) -> None: ...
    async def get_original_interaction_response(
        self, token: str, application_id: str, message_id: int = "@original"
    ) -> dict: ...
    async def edit_interaction_response(
        self, data: dict, token: str, application_id: str, message_id: str = "@original"
    ) -> dict: ...
    async def delete_interaction_response(
        self, token: str, application_id: str, message_id: int = "original"
    ) -> None: ...
    async def _post_followup(self, data: dict, token: str, application_id: str) -> dict: ...
