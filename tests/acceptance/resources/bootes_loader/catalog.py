"""
A mock catalog support library.
"""

import abc

SUPPORTED_CATALOGS = [
    "AHF",
    "FOF",
    "ROCKSTAR",
    "HBT+",
    "HBT-HERONS",
    "SUBFIND",
]


def load_catalog(catalog_name, catalog_type, path, snapshot, fields):
    """
    Load data from anyone of the supported halo catalogs.

    :param catalog_name: The name of the catalog. Must be one of the
        supported catalogs. See :const:`SUPPORTED_CATALOGS` for options.
    :type catalog_name: str
    :param catalog_type: The type of catalog, i.e. the file structure of
        the catalog files.
    :type catalog_type: Literal['snapshot', 'merger tree']
    :param path: The path to the catalog directory. Must contain the
        directory or source file for the chosen snapshot.
    :type path: str | os.PathLike
    :param snapshot: The snapshot to load.
    :type snapshot: int
    :param fields: A list of fields to load from the catalog. See the
        documentation for the respective catalog to find supported fields.
    :type fields: list[str]
    :raises KeyError: When a field was requested that is not supported
        by the chosen catalog.
    :return: A mapping of field names to the respective values as
        arrays.
    :rtype: dict[str, NDArray[Any]]
    """
    pass


class Catalog(abc.ABC):
    """
    An abstract base class for catalogs.

    The class provides abstract methods that implementations for each of
    the supported halo catalogs must implement. You can add support for
    your own catalog by implementing this abstract base class.

    .. caution::

        Any catalog from :const:`SUPPORTED_CATALOGS` that does not
        have an associated catalog subclass will cause importing the
        package to raise an exception.
    """

    @abc.abstractmethod
    def load_catalog(self, path, structure, snapshot):
        """
        Function to load the catalog from file.

        The function **must** return the full raw file content of the
        given snapshot. Fields are filtered only later in the
        :meth:`extract_fields` method.

        :param path: Path to the directory of the catalog file.
        :type path: str | os.PathLike
        :param structure: Structure of the catalog file.
        :type structure: str | None
        :param snapshot: The number of the snapshot.
        :type snapshot: int
        :return: The full raw file content of the catalog for the given
            snapshot.
        :rtype: Any
        """
        pass
