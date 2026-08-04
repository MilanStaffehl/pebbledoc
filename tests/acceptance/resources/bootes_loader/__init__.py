"""
Bootes is a Python library to help load various halo catalogs.

Note that this is not a real package, and it only exists as fixture for
the ``minidoc-md`` package. As opposed to ``stellarium_lite``, this one
is entirely untyped and relies on docstring for type hints.

    "My disappointment is immeasurable, and my day is ruined."

    -- Someone expecting a real halo loading package.

:author: Milan Staffehl
:copyright: 2026 Milan Staffehl
"""

from .catalog import SUPPORTED_CATALOGS, Catalog, load_catalog

__all__ = ["SUPPORTED_CATALOGS", "Catalog", "load_catalog"]
