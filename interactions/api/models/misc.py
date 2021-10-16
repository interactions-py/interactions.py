# TODO: Reorganise these models based on which big obj uses little obj
# TODO: Potentially rename some model references to enums, if applicable
# TODO: Reorganise mixins to its own thing, currently placed here because circular import sucks.
# also, it should be serialiser* but idk, fl0w'd say something if I left it like that. /shrug


class DictSerializerMixin(object):
    """
    The purpose of this mixin is to be subclassed.

    ..note::

        On subclass, it:
            -- From kwargs (received from the Discord API response), add it to the `_json` attribute
            such that it can be reused by other libraries/extensions
            -- Aids in attributing the kwargs to actual model attributes, i.e. `User.id`
            -- Dynamically sets attributes not given to kwargs but slotted to None, signifying that it doesn't exist.

    ..warning::

        This does NOT convert them to its own data types, i.e. timestamps, or User within Member. This is left by
        the object that's using the mixin.
    """

    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])
        self._json = kwargs

        if hasattr(
            self, "__slots__"
        ):  # TODO: Somehow reference pyi typehinting slots. Without the ref., it can be N/A.
            for _attr in self.__slots__:
                if not hasattr(self, _attr):
                    setattr(self, _attr, None)


class Overwrite(DictSerializerMixin):
    """This is used for the PermissionOverride obj"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ClientStatus(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
