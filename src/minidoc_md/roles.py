"""
Module to help register roles not natively understood by docutils.

Sphinx-style docstrings allow roles that docutils does not natively
support, specifically the language-specific roles such as ``:meth_``
or ``:class:``. This module provides a function to register these
roles.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

from docutils import nodes
from docutils.parsers.rst import roles

if TYPE_CHECKING:
    from docutils.parsers.rst.states import Inliner


class SphinxRef(nodes.Inline, nodes.TextElement):
    """
    Node for Sphinx-style reference roles.
    """

    pass


def _sphinx_ref_role(
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: Inliner,
    options: Mapping[str, Any] | None = None,
    content: Sequence[str] | None = None,
) -> tuple[Sequence[nodes.reference], Sequence[nodes.reference]]:
    """
    Role interpreter for Sphinx-style reference roles.

    :param name: The local name of the interpreted text role, the role
        name actually used in the document.
    :param rawtext: A string containing the entire interpreted text
        construct. Return it as a ``problematic`` node linked to a system
        message if there is a problem.
    :param text: The interpreted text content, with backslash escapes
        converted to nulls (``\x00``).
    :param lineno: The line number where the text block containing the
        interpreted text begins.
    :param inliner: The Inliner object that called the role function.
        It defines the following useful attributes: ``reporter``,
        ``problematic``, ``memo``, ``parent``, ``document``.
    :param options: A dictionary of directive options for customization,
        to be interpreted by the role function.  Used for additional
        attributes for the generated elements and other functionality.
    :param content: A list of strings, the directive content for
        customization ("role" directive).  To be interpreted by the role
        function.
    :return: Tuple of two values:

        - A list of nodes which will be inserted into the document tree
          at the point where the interpreted role was encountered (can
          be an empty list).
        - A list of system messages, which will be inserted into the
          document tree immediately after the end of the current inline
          block (can also be empty).
    """
    match = re.match(r"^(.*)<(.*)>$", text)
    if match:
        display_name, target = match.group(1).strip(), match.group(2).strip()
    else:
        display_name, target = text, text

    no_ref = target.startswith("!")
    shortened_name = target.startswith("~")
    target = target.lstrip("~")
    target = target.rstrip("!")

    # do not render links to any private members
    includes_private = any([x.startswith("_") for x in target.split(".")])

    if shortened_name:
        display_name = target.split(".")[-1]
        display_name = display_name.lstrip("~")  # just in case...
    if no_ref:
        display_name = display_name.lstrip("!")

    if no_ref or includes_private:
        node = SphinxRef(rawtext, display_name)
    else:
        node = SphinxRef(rawtext, display_name, target=target, reftype=name)
    return [node], []  # pyrefly: ignore[bad-return]


def register_sphinx_reference_roles() -> None:
    """
    Register all known Sphinx Python-domain roles.

    :return: None.
    """
    sphinx_roles = [
        "mod",
        "func",
        "deco",
        "data",
        "const",
        "class",
        "meth",
        "attr",
        "type",
        "exc",
        "obj",
    ]
    for role in sphinx_roles:
        roles.register_local_role(role, _sphinx_ref_role)
