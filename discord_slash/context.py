from discord.ext.commands import Context
from discord.utils import cached_property

class Context(Context):
    def __init__(self, **attrs):
        self.interaction = attrs.pop('interaction', None)
        if self.interaction is not None:
            attrs['message'] = self.interaction
        super().__init__(**attrs)
        if self.interaction is not None:
            self.message = None

    def _get_channel(self):
        if self.interaction is not None:
            return self.interaction.channel
        return super()._get_channel()

    @cached_property
    def guild(self):
        if self.interaction is not None:
            return self.interaction.guild
        return self.message.guild

    @cached_property
    def channel(self):
        if self.interaction is not None:
            return self.interaction.channel
        return self.message.channel

    @cached_property
    def author(self):
        if self.interaction is not None:
            return self.interaction.member
        return self.message.author

    def reply(self, *args, **kwargs):
        if self.interaction is not None:
            raise TypeError('Can\'t reply to interaction command')
        return super().reply(*args, **kwargs)       

    def callback(self, *args, **kwargs):
        if self.interaction is None:
            raise TypeError('Can\'t call callback of non-interaction command')
        return self.interaction.callback(*args, **kwargs)

    def send(self, *args, **kwargs):
        if self.interaction is not None:
            return self.interaction.send(*args, **kwargs)
        return super().send(*args, **kwargs)