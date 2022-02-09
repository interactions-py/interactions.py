class Converter:
    """
    A class representing the "conversion" or consistent mapping between
    two objects' attributes.
    """

    __slots__ = ("_obj1", "_obj2")

    def __init__(self, __obj1: object, __obj2: object) -> None:
        self._obj1 = __obj1
        self._obj2 = __obj2
        self._map_attr()

    def _map_attr(self) -> None:
        """Maps the attributes of the two objects for conversion."""
        ...
