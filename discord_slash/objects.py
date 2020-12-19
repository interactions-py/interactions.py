from discord import Guild
from discord import Integration
from discord import Member
from .application import IntegrationApplication

class Integration(Integration):
    def _form_data(self, integ):
        super()._form_data(integ)
        self.subscriber_count = data.get('subscriber_count')
        self.revoked = data.get('revoked')
        self.application = IntegrationApplication(state=self._state, data=integ.get('application'))

class Guild(Guild):
    async def integrations(self):
        data = await self._state.http.get_all_integrations(self.id)
        return [Integration(guild=self, data=d) for d in data]

class PartialMember(Member):
    def __init__(self, *args, **kwargs):
        self._guild = None
        super().__init__(*args, **kwargs)
    
    @property
    def guild(self):
        if self._guild is None:
            raise AttributeError('{} is missing guild.'.format(self.__class__.__name__))
        return self._guild
    
    @guild.setter
    def guild(self, guild):
        self._guild = guild