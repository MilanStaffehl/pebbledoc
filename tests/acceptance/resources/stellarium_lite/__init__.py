"""
A tiny mock astronomy package used to exercise an RST-to-Markdown docstring renderer.

This package is not a real astronomy library -- every function is a stub and
every constant is arbitrary. It exists purely as a fixture.
"""

from . import observation
from .catalog import DEFAULT_CATALOG_NAME, CelestialObject, Star, load_catalog

__all__ = [
    "observation",
    "DEFAULT_CATALOG_NAME",
    "load_catalog",
    "CelestialObject",
    "Star",
]
