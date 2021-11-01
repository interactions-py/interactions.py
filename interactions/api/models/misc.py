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

    __slots__ = "_json"

    def __init__(self, **kwargs):
        self._json = kwargs
        for key in kwargs:
            setattr(self, key, kwargs[key])

        if self.__slots__ is not None:  # safeguard
            for _attr in self.__slots__:
                if not hasattr(self, _attr):
                    setattr(self, _attr, None)


class Overwrite(DictSerializerMixin):
    """
    This is used for the PermissionOverride object.

    :ivar int id: Role or User ID
    :ivar int type: Type that corresponds ot the ID; 0 for role and 1 for member.
    :ivar str allow: Permission bit set.
    :ivar str deny: Permission bit set.
    """

    __slots__ = ("_json", "id", "type", "allow", "deny")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ClientStatus(DictSerializerMixin):
    """
    An object that symbolizes the status per client device per session.

    :ivar typing.Optional[str] desktop: User's status set for an active desktop application session
    :ivar typing.Optional[str] mobile: User's status set for an active mobile application session
    :ivar typing.Optional[str] web: User's status set for an active web application session
    """

    __slots__ = ("_json", "desktop", "mobile", "web")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
