"""
Observation planning and session bookkeeping.

Tools in this module build on :mod:`catalog` to decide *what* is worth
looking at on a given night, and record *what was actually seen*.

    Plans are only ever approximations of what the sky will actually do.

This module also defines :class:`ObservableMixin`, an abstract interface
used by :class:`HybridObject` below.

.. comment

   Kept deliberately short; catalog.py carries most of the narrative detail.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import ClassVar, Final

from ..catalog import CelestialObject, Star

#: Faintest magnitude this package will bother scheduling.
MAX_MAGNITUDE: Final[float] = 30.0


# pyrefly: ignore[bad-return]
def plan_session(objects: list, *, start_at: int = 3) -> list:
    """
    Build an ordered observation plan for a night.

    Objects are grouped by priority tier:

    1. Must-see targets
    2. Nice-to-have targets

       1. Bright nice-to-haves
       2. Faint nice-to-haves

    3. Filler targets

    Numbering can also resume mid-sequence when appending to an existing
    plan, e.g. a plan continued from item 3:

    3. Re-check M42
    4. Re-check M31

    See `NASA`_ for some real-world astronomy.

    .. _NASA: https://www.nasa.gov/

    :param objects: Candidate :class:`CelestialObject` instances.
    :param start_at: Priority tier to begin scheduling from.
    :returns: A list of objects in observation order.
    """
    pass


# pyrefly: ignore[bad-return]
def _score_visibility(obj: CelestialObject) -> float:
    """Score how worth-observing an object is right now."""
    pass


class ObservableMixin(abc.ABC):
    """
    Abstract interface for anything that can report its own visibility.

    .. important::

       Subclasses **must** implement :meth:`observe`; the base class raises
       ``NotImplementedError`` otherwise via the ``abstractmethod`` machinery.

    .. versionadded:: 0.1.0
    """

    @abc.abstractmethod
    def observe(self) -> Observation:
        """
        Perform an observation and return the resulting record.

        :returns: A new :class:`Observation`.
        """
        raise NotImplementedError


class VariableStar(Star):
    """
    A star whose brightness changes over time.

    Extends :class:`Star`, which in turn extends :class:`CelestialObject`.

    .. code:: text

        night 1: mag 3.2
        night 2: mag 3.6
        night 3: mag 3.1

    Compare with the equivalent, more explicit directive:

    .. code-block:: python

        history = [3.2, 3.6, 3.1]
        amplitude = max(history) - min(history)

    :param period_days: Approximate variability period, in days.
    """

    def __init__(
        self,
        name: str,
        ra: float,
        dec: float,
        magnitude: float,
        period_days: float,
    ) -> None:
        super().__init__(name, ra, dec, magnitude)
        self.period_days = period_days


class HybridObject(CelestialObject, ObservableMixin):
    """
    An object that is both a :class:`CelestialObject` and
    :class:`ObservableMixin`.

    .. hint::

       This class mostly exists to exercise multiple inheritance; prefer
       :class:`~Star` or :class:`VariableStar` for real use.
    """

    def observe(self) -> Observation:  # pyrefly: ignore[bad-return]
        """Perform an observation of this hybrid object.

        :returns: A new :class:`Observation` record.
        """
        pass


@dataclass
class Observation:
    """
    A single recorded observation.

    :param object_name: Name of the object observed, e.g. ``"M31"``.
    :param magnitude: Estimated visual magnitude at time of observation.
    :param tags: Free-form labels attached to this observation.
    """

    #: Schema version for on-disk serialization of ``Observation`` records.
    schema_version: ClassVar[int] = 1

    object_name: str
    magnitude: float = 0.0
    tags: list = field(default_factory=list)
