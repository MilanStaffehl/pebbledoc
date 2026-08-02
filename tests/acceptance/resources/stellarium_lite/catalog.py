"""Catalog lookup and object modeling.

This module provides the core :class:`CelestialObject` hierarchy along with
helpers for loading catalog data. It is loosely inspired by the *Messier*
and *NGC* catalogs, though no real astronomical data is included here.

    "Somewhere, something incredible is waiting to be known."

    -- Carl Sagan

See the `Messier catalog <https://en.wikipedia.org/wiki/Messier_object>`_
for background, or just browse https://www.python.org while you wait for
your telescope to cool down.

A minimal usage example:

>>> obj = CelestialObject(name="M31", ra=10.68, dec=41.27)
>>> obj.kind
'unknown'

.. comment

   This whole docstring is a fixture; none of the "history" below is real.
"""

from __future__ import annotations

from typing import ClassVar, Final

#: Default catalog used when none is specified.
DEFAULT_CATALOG_NAME: Final[str] = "Messier"


# pyrefly: ignore[bad-return]
def load_catalog(name: str = DEFAULT_CATALOG_NAME) -> dict:
    """Load a named catalog of celestial objects.

    Supported catalogs, in rough order of popularity:

    1. Messier
    2. NGC
    3. IC

    Within each catalog, objects are grouped as:

    - Galaxies

      - Spiral
      - Elliptical

    - Nebulae
    - Star clusters

    Catalog metadata for the default catalog:

    :Author: Charles Messier
    :Year: 1774
    :Publisher: Académie royale des sciences

    A *very* small excerpt of the raw format looks like this::

        M31,Andromeda Galaxy,10.68,41.27
        M42,Orion Nebula,83.82,-5.39

    .. tip::

       Catalog files are cached on first load; see :func:`~catalog._normalize_name`
       for how lookup keys are derived.

    .. versionadded:: 0.2.0

    :param name: The catalog identifier, e.g. ``"Messier"``.
    :returns: A ``dict`` mapping object names to raw records.
    """
    pass


# pyrefly: ignore[bad-return]
def _normalize_name(name: str) -> str:
    """Normalize a catalog name for lookup."""
    pass


class CelestialObject:
    """Base class for anything you can point a telescope at.

    A :class:`CelestialObject` tracks basic **positional** information --
    right ascension and declination -- along with an optional *kind* label.
    Positions are expressed in degrees, following the convention
    :math:`0^\\circ \\le \\alpha < 360^\\circ` for right ascension.

    .. attention::

       Coordinates are assumed to use the J2000 epoch. Mixing epochs will
       silently produce wrong results.

    .. danger::

       Do not pass declinations outside :math:`[-90^\\circ, 90^\\circ]` --
       downstream trigonometry will raise or, worse, return nonsense.

    .. caution::

       Instances are **not** thread-safe; see :attr:`kind` mutation in
       :meth:`_recompute`.

    .. versionchanged:: 0.3.0

       ``ra`` and ``dec`` are now stored in degrees instead of radians.
    """

    #: Default classification for newly constructed objects.
    kind: ClassVar[str] = "unknown"

    def __init__(self, name: str, ra: float, dec: float) -> None:
        self.name = name
        self.ra = ra
        self.dec = dec

    @property
    def is_visible(self) -> bool:  # pyrefly: ignore[bad-return]
        """``bool``: Whether the object is currently above the horizon.

        This is a naive placeholder -- see :class:`~observation.ObservableMixin`
        for the real visibility logic used elsewhere in this package.
        """
        pass

    # pyrefly: ignore[bad-return]
    def describe(self, *, verbose: bool = False) -> str:
        """Return a short human-readable description.

        Uses the object's right ascension (in h \\ :sup:`m` \\ :sup:`s`
        notation) and declination (in degrees, with :sub:`J2000` epoch
        implied) to build a one-line summary.

        :param verbose: If ``True``, include catalog metadata as well.
        :returns: A description such as ``"M31 (unknown)"``.
        """
        pass

    def _recompute(self) -> None:
        """Recompute cached derived fields."""
        pass

    @classmethod
    def from_dict(
        cls, record: dict
    ) -> CelestialObject:  # pyrefly: ignore[bad-return]
        """Build a :class:`CelestialObject` from a raw catalog record.

        :param record: A mapping with at least ``name``, ``ra``, ``dec`` keys.
        :returns: A new instance of ``cls``.
        """
        pass

    @staticmethod
    # pyrefly: ignore[bad-return]
    def angular_separation(a: CelestialObject, b: CelestialObject) -> float:
        """Compute the angular separation between two objects, in degrees.

        Uses the standard great-circle formula

        .. math::

            \\cos(d) = \\sin(\\delta_1)\\sin(\\delta_2)
            + \\cos(\\delta_1)\\cos(\\delta_2)\\cos(\\alpha_1 - \\alpha_2)

        :param a: The first object.
        :param b: The second object.
        :returns: Separation ``d`` in degrees.
        """
        pass


class Star(CelestialObject):
    """A single star, extending :class:`!CelestialObject` with a magnitude.

    See also :mod:`catalog` for how instances are typically constructed via
    :func:`load_catalog`.
    """

    def __init__(
        self, name: str, ra: float, dec: float, magnitude: float
    ) -> None:
        super().__init__(name, ra, dec)
        self.magnitude = magnitude
