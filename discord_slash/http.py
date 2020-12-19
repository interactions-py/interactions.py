import asyncio

from discord.http import (
    HTTPClient,
    Route
)

class HTTPClient(HTTPClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_info = None
        self._app_info_event = asyncio.Event()

    async def static_login(self, *args, **kwargs):
        data = await super().static_login(*args, **kwargs)
        if self.bot_token:
            self.app_info = await self.application_info()
            self._app_info_event.set()
        return data

    def get_application_commands(self, application_id, guild_id=None):
        if guild_id is None:
            r = Route('GET', '/applications/{application_id}/commands', application_id=application_id)
        else:
            r = Route('GET', '/applications/{application_id}/guilds/{guild_id}/commands')

        return self.request(r)

    def create_application_command(self, application_id, guild_id=None, data=None):
        if guild_id is None:
            r = Route('POST', '/applications/{application_id}/commands', application_id=application_id)
        else:
            r = Route('POST', '/applications/{application_id}/guilds/{guild_id}/commands', application_id=application_id, guild_id=guild_id)

        return self.request(r, json=data)

    def edit_application_command(self, application_id, command_id, guild_id=None, **options):
        if guild_id is None:
            r = Route('PATCH', '/applications/{application_id}/commands/{command_id}', application_id=application_id, command_id=command_id)
        else:
            r = Route('PATCH', '/applications/{application_id}/guilds/{guild_id}/commands/{command_id}', application_id=application_id, command_id=command_id, guild_id=guild_id)

        payload = options
        
        if name is not None:
            payload['name'] = name

        if description is not None:
            payload['description'] = description

        return self.request(r, json=payload)

    def delete_application_command(self, application_id, command_id, guild_id=None):
        if guild_id is None:
            r = Route('DELETE', '/applications/{application_id}/commands/{command_id}', application_id=application_id, command_id=command_id)
        else:
            r = Route('DELETE', '/applications/{application_id}/guilds/{guild_id}/commands/{command_id}', application_id=application_id, guild_id=guild_id, command_id=command_id)

    def create_interaction_response(self, interaction_id, interaction_token, interaction_response):
        r = Route('POST', '/interactions/{interaction_id}/{interaction_token}/callback', interaction_id=interaction_id, interaction_token=interaction_token)

        return self.request(r, json=interaction_response)