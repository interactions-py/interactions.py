# TODO: Reorganise these models based on which big obj uses little obj
# TODO: Potentially rename some model references to enums, if applicable
# TODO: Reorganise mixins to its own thing, currently placed here because circular import sucks.
# also, it should be serialiser* but idk, fl0w'd say something if I left it like that. /shrug
import datetime
from typing import Union


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


class Snowflake(object):
    """
    The Snowflake object.

    This snowflake object will have features closely related to the
    API schema. In turn, compared to regular d.py's treated snowflakes,
    these will be treated as strings.


    (Basically, snowflakes will be treated as if they were from d.py 0.16.12)

    ..note::
        You can still provide integers to them, to ensure ease of use of transition and/or
        if discord API for some odd reason will switch to integer.
    """

    # TODO: Should this inherit from the mixin?

    __slots__ = "_snowflake"
    # Slotting properties are pointless, they are not in-memory
    # and are instead computed in-model.

    def __init__(self, snowflake: Union[int, str, "Snowflake"]) -> None:
        self._snowflake = str(snowflake)

    def __str__(self):
        # This is overridden for model comparison between IDs.
        return self._snowflake

    @property
    def increment(self) -> int:
        """
        This is the 'Increment' portion of the snowflake.
        This is incremented for every ID generated on that process.

        :return: An integer denoting the increment.
        """
        return int(self._snowflake) & 0xFFF

    @property
    def worker_id(self) -> int:
        """
        This is the Internal Worker ID of the snowflake.
        :return: An integer denoting the internal worker ID.
        """
        return (int(self._snowflake) & 0x3E0000) >> 17

    @property
    def process_id(self) -> int:
        """
        This is the Internal Process ID of the snowflake.
        :return: An integer denoting the internal process ID.
        """
        return (int(self._snowflake) & 0x1F000) >> 12

    @property
    def epoch(self) -> float:
        """
        This is the "Timestamp" field of the snowflake.

        :return: A float containing the seconds since Discord Epoch.
        """
        return ((int(self._snowflake) >> 22) + 1420070400000) / 1000

    @property
    def timestamp(self) -> datetime.datetime:
        """
        The Datetime object variation of the the "Timestamp" field of the snowflake.

        :return: The converted Datetime object from the Epoch. This respects UTC.
        """
        return datetime.datetime.utcfromtimestamp(self.epoch)

    # ---- Extra stuff that might be helpful.

    def __hash__(self):
        return hash(self._snowflake)

    # Do we need not equals, equals, gt/lt/ge/le?
    # If so, list them under. By Discord API this may not be needed
    # but end users might.
