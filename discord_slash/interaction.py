import aiohttp

from discord import (
    Webhook,
    AsyncWebhookAdapter
)

from .objects import PartialMember

class InteractionCallbackType:
    pong = 1
    acknowledge = 2
    channel_message = 3
    channel_message_with_source = 4
    ack_with_source = 5

class Interaction(Webhook):
    def __init__(self, *, state, data):
        self.__state = state
        self._client_session = aiohttp.ClientSession() 
        adapter = AsyncWebhookAdapter(session=self._client_session)
        super().__init__(data=data, adapter=adapter)
        self.author = PartialMember(state=state, data=data.pop('member'), guild=self.guild)
        self.interaction_id = self.id
        self.id = self.__state.integration_app_info.id
        self._adapter._prepare(self)
        self.data = ApplicationCommandInteractionData(data=data.get('data'))
        self.version = data.get('version')

    async def callback(self, content=None, *, tts=False, embeds=None, allowed_mentions=None, callback_type=InteractionCallbackType.channel_message):
        payload = {
            'type': callback_type
        }
        if callback_type not in (InteractionCallbackType.acknowledge, InteractionCallbackType.ack_with_source):
            if embeds is not None:
                embeds = [
                    embed.to_dict() 
                    for embed in embeds
                ]
            else:
                embeds = []
            
            if allowed_mentions is not None:
                allowed_mentions = allowed_mentions.to_dict()

            data = {
                'content': str(content),
                'tts': tts,
                'emebds': embeds,
                'allowed_mentions': allowed_mentions
            }
            payload['data'] = data
        await self.__state.http.create_interaction_response(self.interaction_id, self.token, payload)

class ApplicationCommandInteractionData:
    def __init__(self, data):
        self.id = int(data.get('id'))
        self.name = data.get('name')
        self.options = []
        options = data.get('options', [])
        for option in options:
            self.options.append(ApplicationCommandInteractionDataOption(data=option))

class ApplicationCommandInteractionDataOption:
    def __init__(self, data):
        self.name = data.get('name')
        self.value = data.get('value')
        self.options = []
        options = data.get('options', [])
        for option in options:
            self.options.append(ApplicationCommandInteractionDataOption(data=option))

class InteractionResponse:
    def __init__(self, data):
        self.type = data.get('type')
        self.data = data.get('data')

class InteractionType:
    ping = 1
    application_command = 2