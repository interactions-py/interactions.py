from typing import List


class Converter:
    """
    A class representing the "conversion" or consistent mapping between
    two objects' attributes.

    :ivar object _obj1: The first object to be converted.
    :ivar object _obj2: The second object to be converted.
    """

    __slots__ = ("_obj1", "_obj2")

    def __init__(self, __obj1: object, __obj2: object) -> None:
        """
        :param __obj1: The first object to be converted.
        :type __obj1: object
        :param __obj2: The second object to be converted.
        :type __obj2: object
        """
        self._obj1 = __obj1
        self._obj2 = __obj2
        self._map_attr()

    def __repr__(self) -> str:
        return self._obj2

    def _map_attr(self) -> dict:
        """
        Maps the attributes between the models for conversion reference.

        :return: A dictionary of attributes mapped.
        :rtype: dict
        """
        for attr1 in self._obj1.keys():
            for attr2 in self._obj2.keys():
                self.__dict__.update({attr1: attr2})

        return self.__dict__

    def get_attr(self, attr: str) -> str:
        """
        Gets a mapped attribute.

        :param attr: The attribute to get.
        :type attr: str
        :return: The mapped attribute.
        :rtype: str
        """
        return self.__dict__.get(attr)

    def get_attrs(self) -> List[str]:
        """
        Gets a list of mapped attributes.

        :return: The list of mapped attributes.
        :rtype: list
        """
        return self.__dict__

    @property
    def ref(self) -> object:
        """
        Gets the "referenced" model, or first.

        :return: The referenced model.
        :rtype: object
        """
        return self._obj1

    @property
    def difference(self) -> List[dict]:
        """
        Gets a list of keys and values that the models don't share in common.

        :return: A list of dictionaries
        :rtype: List[dict]
        """
        return [{key: val} for key, val in self._obj2 if key not in self._obj1]

    @property
    def missing(self) -> List[dict]:
        """
        Gets a list of keys and values missing from the "referenced" or first model.

        :return: A list of dictionaries
        :rtype: List[dict]
        """
        return [{key: val} for key, val in self._obj1 if key not in self._obj2]
