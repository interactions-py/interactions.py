from .misc import DictSerializerMixin


class RoleTags(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Role(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
