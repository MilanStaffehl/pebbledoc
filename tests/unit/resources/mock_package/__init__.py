"""
Mock package for unit testing.

We primarily test member discovery in cases where __all__ is not provided.
"""

# ruff: noqa: F401
# some external libraries (none of them should show up in list of members)
import logging.config
import sys
from pathlib import Path

from docutils import nodes

# re-export some own members: submodule_a/c crucially should NOT show up!
from . import submodule_b
from .submodule_a import MyClass, my_function
from .submodule_c import UnwieldyNamePlsRename as BetterClassName
from .subpackage import direct_module


class TopLevelClass:  # should show up
    pass


def top_level_function():  # should also show up
    pass
