"""
pebbledoc offers utilities for creating documentation.

Primarily, ``pebbledoc`` acts as a command line interface (CLI) tool to
create GitHub-flavored Markdown documentation. See the README of the
project for details or run ``pebbledoc --help`` to get an overview over
its functionalities.

However, for convenience, ``pebbledoc`` also exposes some of its more
generally useful functions for programmatic use in Python scripts and
libraries.
"""

from .directives import register_sphinx_version_notice_directives
from .documenting import markdown_documentation
from .inspect_runtime import discover_public_members
from .parsing import parse_docstring
from .roles import register_sphinx_reference_roles

# metadata
__version__ = "0.2.0"
__author__ = "Milan Staffehl"
__email__ = "milan.staffehl@gmail.com"
__copyright__ = "(c) Milan Staffehl 2026"

# API
__all__ = [
    "discover_public_members",
    "parse_docstring",
    "markdown_documentation",
]

# register Sphinx roles and directives - always required
register_sphinx_reference_roles()
register_sphinx_version_notice_directives()
