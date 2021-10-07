from .misc import DictSerializerMixin


class User(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
