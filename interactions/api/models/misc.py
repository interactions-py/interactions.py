# TODO: Reorganise these models based on which big obj uses little obj
# TODO: Potentially rename some model references to enums, if applicable
# TODO: Reorganise mixins to its own thing, currently placed here because circular import sucks.
# also, it should be serialiser* but idk, fl0w'd say something if I left it like that. /shrug
# kazam and crash, your opinion is trash ^


class DictSerializerMixin(object):
    """
    The purpose of this mixin is to be subclassed.

    ..note::

        On subclass, it:
            -- From kwargs (received from the Discord API response), add it to the `_json` attribute
            such that it can be reused by other libraries/extensions
            -- Aids in attributing the kwargs to actual model attributes, i.e. `User.id`

    ..warning::

        This does NOT convert them to its own data types, i.e. timestamps, or User within Member. This is left by
        the object that's using the mixin.
    """

    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])
        self._json = kwargs


class Overwrite(DictSerializerMixin):
    """This is used for the PermissionOverride obj"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ClientStatus(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Format(object):
    """
    This object is used to respectively format markdown strings
    provided by the WYSIWYG text editor for ease-of-accessibility
    and simple implementations into bots.

    .. note::
        All base strings are given brackets before being f-string
        parsable to make conversion simplified.

    .. warning::
        the ``stylize()`` method must be used if you're actually
        looking to give a **str** specific result.
    """

    def stylize(self, format: str, **kwargs) -> str:
        r"""
        This takes a format style from the object and
        converts it into a useable string for ease.

        :param format: The format string to use.
        :type format: str
        :param \**kwargs: Multiple key-word arguments to use, where key=value is format=value.
        :type \**kwargs: dict
        :return: str
        """
        new: str = f""  # noqa: F541
        for kwarg in kwargs:
            if format == kwarg:
                new = new + format
        return new
