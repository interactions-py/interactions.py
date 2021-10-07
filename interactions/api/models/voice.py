from .misc import DictSerializerMixin


class VoiceState(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class VoiceRegion(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
