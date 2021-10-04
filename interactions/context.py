from .api.models.misc import DictSerializerMixin


class Context(DictSerializerMixin):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


class InteractionContext(Context):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


class ComponentContext(InteractionContext):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
