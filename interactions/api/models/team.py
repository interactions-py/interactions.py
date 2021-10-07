from .misc import DictSerializerMixin


class TeamMember(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Team(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Application(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
