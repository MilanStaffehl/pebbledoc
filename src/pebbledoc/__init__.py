from .directives import register_sphinx_version_notice_directives
from .inspect_runtime import discover_public_members, markdown_documentation
from .parsing import parse_docstring
from .roles import register_sphinx_reference_roles

# metadata
__version__ = "0.1.0"
__author__ = "Milan Staffehl"
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
