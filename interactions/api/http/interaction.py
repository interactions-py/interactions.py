from typing import TYPE_CHECKING, List, Optional, Union

from aiohttp import MultipartWriter

from ..models import Snowflake
from ..models.message import File
from .request import _Request
from .route import Route

if TYPE_CHECKING:
    from ...api.cache import Cache

__all__ = ("InteractionRequest",)


class InteractionRequest:
    _req: _Request
    cache: "Cache"

    def __init__(self) -> None:
        pass

    async def get_application_commands(
        self,
        application_id: Union[int, Snowflake],
        guild_id: Optional[int] = None,
        with_localizations: Optional[bool] = None,
    ) -> List[dict]:
        """
        Get all application commands from an application.

        :param application_id: Application ID snowflake
        :param guild_id: Guild to get commands from, if specified. Defaults to global (None)
        :param with_localizations: Whether to include full localization dictionaries (name_localizations and description_localizations) in the returned objects, instead of the name_localized and description_localized fields. Default false.
        :return: A list of Application commands.
        """
        application_id = int(application_id)

        params = {}

        if with_localizations:
            params["with_localizations"] = f"{with_localizations}"

        if guild_id in (None, "None"):
            return await self._req.request(
                Route("GET", f"/applications/{application_id}/commands"), params=params
            )
        else:
            return await self._req.request(
                Route("GET", f"/applications/{application_id}/guilds/{guild_id}/commands"),
                params=params,
            )

    async def create_application_command(
        self, application_id: Union[int, Snowflake], data: dict, guild_id: Optional[int] = None
    ) -> dict:
        """
        Registers to the Discord API an application command.

        :param application_id: Application ID snowflake
        :param data: The dictionary that contains the command (name, description, etc)
        :param guild_id: Guild ID snowflake to put them in, if applicable.
        :return: An application command object.
        """

        application_id = int(application_id)

        url = (
            f"/applications/{application_id}/commands"
            if guild_id in (None, "None")
            else f"/applications/{application_id}/guilds/{guild_id}/commands"
        )

        return await self._req.request(Route("POST", url), json=data)

    async def overwrite_application_command(
        self, application_id: int, data: List[dict], guild_id: Optional[int] = None
    ) -> List[dict]:
        """
        Overwrites application command(s) from a scope to the new, updated commands.

        .. note::
            This applies to all forms of application commands (slash and context menus)

        :param application_id: Application ID snowflake
        :param data: The dictionary that contains the command (name, description, etc)
        :param guild_id: Guild ID snowflake to put them in, if applicable.
        :return: An array of application command objects.
        """
        url = (
            f"/applications/{application_id}/guilds/{guild_id}/commands"
            if guild_id
            else f"/applications/{application_id}/commands"
        )

        return await self._req.request(Route("PUT", url), json=data)

    async def edit_application_command(
        self,
        application_id: Union[int, Snowflake],
        data: dict,
        command_id: Union[int, Snowflake],
        guild_id: Optional[int] = None,
    ) -> dict:
        """
        Edits an application command.

        :param application_id: Application ID snowflake.
        :param data: A dictionary containing updated attributes
        :param command_id: The application command ID snowflake
        :param guild_id: Guild ID snowflake, if given. Defaults to None/global.
        :return: The updated application command object.
        """
        application_id, command_id = int(application_id), int(command_id)
        r = (
            Route(
                "PATCH",
                "/applications/{application_id}/commands/{command_id}",
                application_id=application_id,
                command_id=command_id,
            )
            if guild_id in (None, "None")
            else Route(
                "PATCH",
                "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
                application_id=application_id,
                command_id=command_id,
                guild_id=guild_id,
            )
        )
        return await self._req.request(r, json=data)

    async def delete_application_command(
        self, application_id: Union[int, Snowflake], command_id: int, guild_id: Optional[int] = None
    ) -> None:
        """
        Deletes an application command.

        :param application_id: Application ID snowflake.
        :param command_id: Application command ID snowflake.
        :param guild_id: Guild ID snowflake, if declared. Defaults to None (Global).
        """

        application_id = int(application_id)

        r = (
            Route(
                "DELETE",
                "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
                application_id=application_id,
                command_id=command_id,
                guild_id=guild_id,
            )
            if guild_id not in (None, "None")
            else Route(
                "DELETE",
                "/applications/{application_id}/commands/{command_id}",
                application_id=application_id,
                command_id=command_id,
            )
        )
        return await self._req.request(r)

    async def edit_application_command_permissions(
        self, application_id: int, guild_id: int, command_id: int, data: List[dict]
    ) -> dict:
        """
        Edits permissions for an application command.

        .. note::
            This requires authenticating with the Bearer token. Likewise, if this function is used in a bot
            process with a bot token, this will fail.

        :param application_id: Application ID snowflake
        :param guild_id: Guild ID snowflake
        :param command_id: Application command ID snowflake
        :param data: Permission data.
        :return: Returns an updated Application Guild permission object.
        """

        return await self._req.request(
            Route(
                "PUT",
                f"/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions",
            ),
            json=data,
        )

    async def get_application_command_permissions(
        self, application_id: int, guild_id: int, command_id: int
    ) -> dict:
        """
        Gets, from the Discord API, permissions from a specific Guild application command.

        :param application_id: Application ID snowflake
        :param guild_id: Guild ID snowflake
        :param command_id: Application Command ID snowflake
        :return: a Guild Application Command permissions object
        """
        return await self._req.request(
            Route(
                "GET",
                f"/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions",
            )
        )

    async def get_all_application_command_permissions(
        self, application_id: int, guild_id: int
    ) -> List[dict]:
        """
        Gets, from the Discord API, permissions from all Application commands at that Guild.

        :param application_id: Application ID snowflake
        :param guild_id: Guild ID snowflake
        :return: An array of Guild Application Command permissions
        """
        return await self._req.request(
            Route("GET", f"/applications/{application_id}/guilds/{guild_id}/commands/permissions")
        )

    async def create_interaction_response(
        self,
        token: str,
        application_id: int,
        data: dict,
        files: Optional[List[File]] = None,
    ) -> None:
        """
        Posts initial response to an interaction, but you need to add the token.

        :param token: Token.
        :param application_id: Application ID snowflake
        :param data: The data to send.
        :param files: The files to send.
        """

        file_data = None
        if files:
            file_data = MultipartWriter("form-data")
            part = file_data.append_json(data)
            part.set_content_disposition("form-data", name="payload_json")
            data = None

            for id, file in enumerate(files):
                part = file_data.append(
                    file._fp,
                )
                part.set_content_disposition(
                    "form-data", name=f"files[{str(id)}]", filename=file._filename
                )

        return await self._req.request(
            Route("POST", f"/interactions/{application_id}/{token}/callback"),
            json=data,
            data=file_data,
        )

    # This is still Interactions, but this also applies to webhooks
    # i.e. overlay
    async def get_original_interaction_response(
        self, token: str, application_id: str, message_id: int = "@original"
    ) -> dict:
        """
        Gets an existing interaction message.

        :param token: token
        :param application_id: Application ID snowflake.
        :param message_id: Message ID snowflake. Defaults to `@original` which represents the initial response msg.
        :return: Message data.
        """
        # ^ again, I don't know if python will let me
        return await self._req.request(
            Route("GET", f"/webhooks/{application_id}/{token}/messages/{message_id}")
        )

    async def edit_interaction_response(
        self,
        data: dict,
        token: str,
        application_id: str,
        files: Optional[List[File]] = None,
        message_id: str = "@original",
    ) -> dict:
        """
        Edits an existing interaction message, but token needs to be manually called.

        :param data: A dictionary containing the new response.
        :param token: the token of the interaction
        :param application_id: Application ID snowflake.
        :param files: The files to send.
        :param message_id: Message ID snowflake. Defaults to `@original` which represents the initial response msg.
        :return: Updated message data.
        """
        # ^ again, I don't know if python will let me
        file_data = None
        if files:
            file_data = MultipartWriter("form-data")
            part = file_data.append_json(data)
            part.set_content_disposition("form-data", name="payload_json")
            data = None

            for id, file in enumerate(files):
                part = file_data.append(
                    file._fp,
                )
                part.set_content_disposition(
                    "form-data", name=f"files[{id}]", filename=file._filename
                )

        return await self._req.request(
            Route("PATCH", f"/webhooks/{application_id}/{token}/messages/{message_id}"),
            json=data,
            data=file_data,
        )

    async def delete_interaction_response(
        self, token: str, application_id: str, message_id: int = "@original"
    ) -> None:
        """
        Deletes an existing interaction message.

        :param token: the token of the interaction
        :param application_id: Application ID snowflake.
        :param message_id: Message ID snowflake. Defaults to `@original` which represents the initial response msg.
        """

        # This is, basically, a helper method for the thing,
        # because interactions are webhooks

        return await self._req.request(
            Route("DELETE", f"/webhooks/{int(application_id)}/{token}/messages/{message_id}")
        )

    async def _post_followup(
        self,
        data: dict,
        token: str,
        application_id: str,
        files: Optional[List[File]] = None,
    ) -> dict:
        """
        Send a followup to an interaction.

        :param data: the payload to send
        :param application_id: the id of the application
        :param token: the token of the interaction
        :param files: the files to send
        """

        file_data = None
        if files:
            file_data = MultipartWriter("form-data")
            part = file_data.append_json(data)
            part.set_content_disposition("form-data", name="payload_json")
            data = None

            for id, file in enumerate(files):
                part = file_data.append(
                    file._fp,
                )
                part.set_content_disposition(
                    "form-data", name=f"files[{id}]", filename=file._filename
                )

        return await self._req.request(
            Route("POST", f"/webhooks/{application_id}/{token}"),
            json=data,
            data=file_data,
        )
