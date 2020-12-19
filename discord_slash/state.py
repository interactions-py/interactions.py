from discord.state import ConnectionState
from discord import AppInfo
from .application import IntegrationApplication
from .objects import Guild
from .interaction import Interaction

class ConnectionState(ConnectionState):
    @property
    def app_info(self):
        if self.http.app_info is None:
            return None
        return AppInfo(state=self, data=self.http.app_info)

    @property
    def integration_app_info(self):
        if self.http.app_info is None:
            return None
        return IntegrationApplication(state=self, data=self.http.app_info, bot=self.user)

    def _add_guild_from_data(self, guild):
        guild = Guild(data=guild, state=self)
        self._add_guild(guild)
        return guild

    def parse_interaction_create(self, data):
        print(data)
        interaction = Interaction(state=self, data=data)
        self.dispatch('interaction_create', interaction)