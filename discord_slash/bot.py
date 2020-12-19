import logging

from discord.ext.commands.bot import BotBase
from discord.ext import commands
from .state import ConnectionState
from .http import HTTPClient
from .context import Context
from .interaction import Interaction
from .context import Context
from .commands import (
    Command,
    GroupMixin
)

log = logging.getLogger(__name__)

class _BotBase(GroupMixin, BotBase):
    pass

class Bot(_BotBase, commands.Bot):
    def __init__(self, *args, **kwargs):
        self.delete_uncreated_application_commands = kwargs.pop('delete_uncreated_application_commands', False)
        connector = kwargs.get('connector')
        proxy = kwargs.get('proxy')
        proxy_auth = kwargs.get('proxy_auth')
        unsync_clock = kwargs.get('unsync_clock')

        self.__http = HTTPClient(connector, proxy=proxy, proxy_auth=proxy_auth, unsync_clock=unsync_clock)

        super().__init__(*args, **kwargs)

        self.http = self.__http

    @property
    def app_info(self):
        return self._connection.app_info
    
    @property
    def integration_app_info(self):
        return self._connection.integration_app_info

    def _get_state(self, **options):
        return ConnectionState(
            dispatch=self.dispatch, handlers=self._handlers, 
            hooks=self._hooks, 
            syncer=self._syncer, 
            http=self.__http, 
            loop=self.loop, 
            **options
        )
    
    async def connect(self, *args, **kwargs):
        if self.http.bot_token:
            await self.http._app_info_event.wait()

            commands = list(self.application_commands.values()) + list(self.mixed_commands.values())

            for command in commands:
                command.application_id = self.integration_app_info.id

                await self.http.create_application_command(command.application_id, command.application_guild_id, command._as_application_command)

        await super().connect(*args, **kwargs)
                
    async def get_context(self, message_or_interaction, cls=Context):
        if isinstance(message_or_interaction, Interaction):
            data = message_or_interaction.data
            commands = dict(list(self.application_commands.items()) + list(self.mixed_commands.items()))
            command = commands.get(data.name)
            invoked_with = data.name
            ctx = cls(interaction=message_or_interaction, command=command, invoked_with=invoked_with, prefix='/', bot=self)
            return ctx
        return await super().get_context(message_or_interaction, cls=Context)

    async def on_interaction_create(self, interaction):
        await self.process_commands(interaction)
        