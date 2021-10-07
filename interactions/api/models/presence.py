from .misc import DictSerializerMixin


class _PresenceParty(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class _PresenceAssets(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class _PresenceSecrets(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class _PresenceButtons(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class PresenceActivity(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class PresenceUpdate(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
