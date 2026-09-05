"""
A tiny mock astronomy package used to exercise an RST-to-Markdown docstring renderer.

There is one sub-package, the :mod:`~stellarium_lite.observation` package.
It holds utilities to handle observational data and plan observations.

This package is not a real astronomy library -- every function is a stub and
every constant is arbitrary. It exists purely as a fixture. If you have any
questions, *don't* send an email to user@example.com!
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
