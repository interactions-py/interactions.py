# Normal libraries
from json import dumps
from typing import (
    Union,
    Optional,
    List,
    Coroutine
)
from aiohttp import FormData
from logging import Logger

# 3rd-party libraries
from discord import (
    Client,
    AutoShardedClient,
    File
)
from discord.http import Route
# from .error import IncorrectFormat
from .base import __api__

class CustomRoute(Route):
    """discord.py's Route with ``BASE`` modified to use current interactions."""
    BASE = __api__

class InteractionHTTP:
    """
    Object representing the base information to be kept for all interaction requests.
    
    :ivar logger:
    :ivar _discord:
    :ivar _application_id:
    """
    logger: Logger
    _discord: Union[Client, AutoShardedClient]
    _application_id: int
    
    def __init__(
        self,
        logger: Logger,
        _discord: Union[Client, AutoShardedClient],
        application_id: Optional[Union[str, int]]=None
    ) -> None:
        """
        Instantiates the InteractionHTTP class.

        :param logger: Logger object for logging events.
        :type logger: logging.Logger
        :param _discord: The discord client to access.
        :type _discord: typing.Union[discord.Client, discord.AutoShardedClient]
        :param application_id: The application ID of the bot.
        :type application_id: typing.Optional[typing.Union[str, int]]
        :return: None
        """
        self.logger: Logger = logger
        self._discord: Union[Client, AutoShardedClient] = _discord
        self._application_id: int = int(application_id) if isinstance(application_id, str) else application_id

    @property
    def application_id(self) -> int:
        """Returns the application ID in literal integer form."""
        return self._application_id if self._application_id else self._discord.user.id

class SlashRequest(InteractionHTTP):
    """
    Object representing slash command requests made to and from the Discord API.

    :inherit: InteractionHTTP
    """
    def __init__(
        self,
        logger,
        _discord,
        application_id=None
    ) -> None:
        """Instantiates the SlashRequest class."""
        super().__init__(
            logger,
            _discord,
            application_id
        )
    
    def request(
        self,
        method: str,
        guild_id: Optional[Union[str, int]]=None,
        url_endswith: Optional[str]="",
        **kwargs
    ) -> Coroutine:
        r"""
        Sends an HTTP request to the Discord API.

        :param method: The HTTP method.
        :type method: str
        :param guild_id: The guild ID to make an HTTP request to. Pass `None` for the global scope.
        :type guild_id: typing.Optional[typing.Union[str, int]]
        :param url_endswith: The ending path of the URL.
        :type url_endswith: typing.Optional[str]
        :param \**kwargs: Keyword-arguments to pass into discord.py's `request function <https://github.com/Rapptz/discord.py/blob/master/discord/http.py#L134>`_
        :return: typing.Coroutine
        """
        url: str = f"/applications/{self.application_id}"
        url += "/commands" if not guild_id else f"/guilds/{guild_id}/commands"
        url += url_endswith if not url_endswith else ""
        route: Coroutine = CustomRoute(method, url)
        return self._discord.http.request(route, **kwargs)

    def command_response(
        self,
        *,
        method: str,
        token: str,
        interaction_id: Optional[int]=None,
        use_webhook: Optional[bool]=False,
        url_endswith: Optional[str]="",
        **kwargs
    ) -> Coroutine:
        r"""
        Sends an HTTP request to the Discord API.

        .. note::
            
            This method extends off of `SlashCommandRequest.request()`.

        :param method: The HTTP method.
        :type method: str
        :param token: The interaction token.
        :type token: str
        :param interaction_id: The ID of the interaction instance.
        :type interaction_id: typing.Optional[int]
        :param use_webhook: Whether to use webhooks or not.
        :type use_webhook: typing.Optional[bool]
        :param url_endswith: The ending path of the URL.
        :type url_endswith: typing.Optional[str]
        :param \**kwargs: Keyword-arguments to pass into discord.py's `request function <https://github.com/Rapptz/discord.py/blob/master/discord/http.py#L134>`_
        :return: typing.Coroutine
        """
        if (
            not use_webhook and 
            not interaction_id
        ):
            # raise IncorrectFormat(
            #     "An error has occured here. The interaction_id must be set if use_webhook is set to False."
            # )
            pass
        else:
            request: str = (
                f"/webhooks/{self.application_id}/{token}"
                if use_webhook
                else f"/interactions/{interaction_id}/{token}/callback"
            )
            request += url_endswith if not url_endswith else ""
            route: CustomRoute = CustomRoute(method, request)
            return self._discord.http.request(route, **kwargs)

    def request_files(
        self,
        *,
        method: str,
        token: str,
        response: dict,
        message_id: Optional[str]="@original",
        files: Optional[List[File]]=None,
        url_endswith: Optional[str]=""
    ) -> Coroutine:
        """
        Makes an HTTP request for retrieving files from an interaction/invoked body.
        
        :param method: The HTTP method.
        :type method: str
        :param token: The slash command message token.
        :type token: str
        :param response: The slash command response.
        :type response: dict
        :param files: A list of files to request for. Defaults to `None`.
        :type files: typing.Optional[typing.List[discord.File]]
        :param url_endswith: The ending path of the URL.
        :type url_endswith: typing.Optional[str]
        :return: typing.Coroutine
        """
        form: FormData = FormData()
        form.add_field("payload_json", dumps(response))
        for pos in range(len(files)):
            name: str = f"file{pos if len(files) > 1 else ''}"
            selection: File = files[pos]
            form.add_field(
                name=name,
                value=selection.fp,
                content_type="application/octet-stream",
                filename=selection.filename
            )
        return self.command_response(
            method=method,
            token=token,
            url_endswith=url_endswith,
            data=form,
            files=files
        )

    def add_followup(
        self,
        *,
        response: dict,
        token: str,
        files: Optional[List[File]]=None
    ) -> Coroutine:
        """
        Sends a POST request for slash command followup responses to the API.

        .. note::

            This method extends off of `SlashCommandRequest.command_response()`.

        :param response: The slash command response.
        :type response: dict
        :param token: The slash command message token.
        :type token: str
        :param files: A list of files to send. Defaults to `None`.
        :type files: typing.Optional[typing.List[discord.File]]
        :return: typing.Coroutine
        """
        if files:
            return self.request_files(
                method="POST",
                response=response,
                token=token,
                files=files
            )
        else:
            return self.command_response(
                method="POST",
                token=token,
                use_webhook=True,
                json=response
            )

    def add_initial_response(
        self,
        *,
        response: dict,
        interaction_id: Union[str, int],
        token: str
    ) -> Coroutine:
        """
        Sends a POST request for initial slash command responses to the API.

        .. note::

            For ease of use, ``interaction_id`` is implicitly casted into an integer.

        :param response: The slash command response.
        :type response: dict
        :param interaction_id: The ID of the interaction.
        :type interaction_id: typing.Union[str, int]
        :param token: The slash command message token.
        :type token: str
        :return: typing.Coroutine
        """
        _interaction_id: int = str(interaction_id) if isinstance(interaction_id, str) else interaction_id
        return self.command_response(
            method="POST",
            token=token,
            interaction_id=_interaction_id,
            json=response
        )

    def get_commands(
        self,
        guild_id: Optional[Union[str, int]]=None
    ) -> Coroutine:
        """
        Sends a GET request for slash commands to the API.
        
        :param guild_id: The guild ID to get the slash commands from. Pass `None` for the global scope.
        :type guild_id: typing.Optional[typing.Union[str, int]]
        :return: typing.Coroutine
        """
        return self.request(
            method="GET",
            guild_id=guild_id
        )

    def add_command(
        self,
        name: str,
        description: str,
        options: Optional[list]=None,
        guild_id: Optional[Union[str, int]]=None
    ) -> Coroutine:
        """
        Sends a POST request for slash commands to the API.

        :param name: The name of the slash command.
        :type name: str
        :param description: The description of the slash command.
        :type description: str
        :options: The arguments/so-called "options" of the slash command.
        :type options: typing.Optional[list]
        :param guild_id: The guild ID to register the slash commands under. Pass `None` for the global scope.
        :type guild_id: typing.Optional[typing.Union[str, int]]
        :return: typing.Coroutine
        """
        struct: dict = {
            "name": name,
            "description": description,
            "options": [] if not options else options
        }
        return self.request(
            method="POST",
            guild_id=guild_id,
            json=struct
        )

    def update_commands(
        self,
        commands: list,
        guild_id: Optional[Union[str, int]]=None
    ) -> Coroutine:
        """
        Sends a PUT request for slash commands to the API.
        
        .. warning::
            
            ``commands`` must be a list containing all of the slash commands.

        :param commands: List of slash commands.
        :type commands: list
        :param guild_id: The guild ID to register the slash commands under. Pass `None` for the global scope.
        :type guild_id: typing.Optional[typing.Union[str, int]]
        :return: typing.Coroutine
        """
        return self.request(
            method="PUT",
            guild_id=guild_id,
            json=commands
        )

    def remove_commands(
        self,
        command_id: Union[str, int],
        guild_id: Optional[Union[str, int]]=None
    ) -> Coroutine:
        """
        Sends a DELETE request for slash commands to the API.
        
        :param command_id: The command ID to delete.
        :type command_id: typing.Union[str, int]
        :param guild_id: The guild ID to delete the slash commands from. Pass `None` for the global scope.
        :type guild_id: typing.Optional[typing.Union[str, int]]
        :return: typing.Coroutine
        """
        return self.request(
            method="DELETE",
            guild_id=guild_id,
            url_endswith=f"/{command_id}"
        )

    def get_command_permissions(
        self,
        guild_id: Optional[Union[str, int]]=None
    ) -> Coroutine:
        """
        Sends a GET request for slash commands to the API.

        .. note::

            This method extends off of ``SlashRequest.get_commands()`` for permissions.

        :param guild_id: The guild ID to get the slash command permissions from. Pass `None` for the global scope.
        :type guild_id: typing.Optional[typing.Union[str, int]]
        :return: typing.Coroutine
        """
        return self.request(
            method="GET",
            guild_id=guild_id,
            url_endswith="/permissions"
        )

    def update_command_permissions(
        self,
        permissions: dict,
        guild_id: Optional[Union[str, int]]=None
    ) -> Coroutine:
        """
        Sends a PUT request for slash commands to the API.
        
        .. warning::
            
            ``permissions`` must be a dictionary containing all of the slash command permissions.

        :param permissions: A set of permissions to update the slash command.
        :type permissions: dict
        :param guild_id: The guild ID to delete the slash commands from. Pass `None` for the global scope.
        :type guild_id: typing.Optional[typing.Union[str, int]]
        :return: typing.Coroutine
        """
        return self.request(
            method="PUT",
            guild_id=guild_id,
            url_endswith="/permissions",
            json=permissions
        )

class MessageRequest(SlashRequest):
    """
    Object representing HTTP requests for handling messages made to and from the Discord API.

    :inherit: SlashRequest
    """
    def edit(
        self,
        response: dict,
        token: str,
        message_id: Optional[str]="@original",
        files: Optional[List[File]]=None
    ) -> Coroutine:
        """
        Sends a PATCH request for editing messages to the API.

        :param response: Message body for the edited response.
        :type response: dict
        :param token: The token of the command message.
        :type token: str
        :param message_id: The ID of the message to edit. Defaults to `@original` for the initial message.
        :type message_id: typing.Optional[str]
        :param files: A list of files to pass for uploading as attachments. Defaults to `None`.
        :type files: typing.Optional[typing.List[discord.File]]
        :return: typing.Coroutine
        """
        url: str = f"/messages/{message_id}"
        if files:
            return super().request_files(
                method="PATCH",
                token=token,
                response=response,
                url_endswith=url
            )
        return super().command_response(
            method="PATCH",
            token=token,
            url_endswith=url,
            json=response
        )

    def delete(
        self,
        token: str,
        message_id: Optional[str]="@original"
    ) -> Coroutine:
        """
        Sends a POST request for deleting messages to the API.

        :param token: The token of the command message.
        :type token: str
        :param message_id: The ID of the message to delete. Defaults to `@original` for the initial message.
        :type message_id: typing.Optional[str]
        :return: typing.Coroutine
        """
        return super().command_response(
            method="DELETE",
            token=token,
            url_endswith=f"/messages/{message_id}"
        )