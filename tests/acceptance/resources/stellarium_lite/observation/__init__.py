"""
The observation module contains utilities for orchestrating surveys.
"""

from .session import (
    MAX_MAGNITUDE,
    HybridObject,
    ObservableMixin,
    Observation,
    VariableStar,
    plan_session,
)

__all__ = [
    "MAX_MAGNITUDE",
    "plan_session",
    "ObservableMixin",
    "VariableStar",
    "HybridObject",
    "Observation",
]
