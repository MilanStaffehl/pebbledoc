"""Utilities used in multiple modules."""

from __future__ import annotations

import re


def name_to_ref(name: str) -> str:
    """
    Turn the given object name into a target name.

    Given the name of an object, turn it into a GitHub reference target
    for a header that uses the object name as title.

    Example: an object named ``foo_Bar_BAS`` will be turned into a
    reference ``foo-bar-bas``. Used in a link as ``[ref](#foo-bar-bas)``,
    it will point to a header using the name as title, such as
    ``### foo_Bar_BAS``.

    :param name: The name of the object to be referenced.
    :return: The reference target that points to a header using ``name``
        as title.
    """
    target = re.sub(r"[^a-z0-9\s\-_]", "", name.lower())
    target = target.strip().replace(" ", "-")
    return target


def full_qualified_name(name: str, parent_name: str) -> str:
    """
    Format the name of a member, depending on the parent name.

    If there is a parent name, the format will be ``parent_name.name``,
    otherwise the name is returned as-is.

    :param name: Name of the member.
    :param parent_name: Name of the parent, or an empty string if the
        parent name shall not be added to the formatted name.
    :return: The name of the member, spliced with the parent name, if
        one was given.
    """
    if parent_name:
        return f"{parent_name}.{name}"
    return name


def all_qualified_names(name: str, parent_name: str) -> set[str]:
    """
    Find all qualified names of the member.

    Given a member name and the full qualified name of its parent, this
    function finds the full qualified name of the member and all shortened
    versions of it (i.e. with prefixes removed).

    :param name: Name of the member.
    :param parent_name: Full qualified name of the parent member.
    :return: A list of all names that can refer to the member, from the
        fully qualified name to the name alone, with prefixes successively
        removed.
    """
    full_name = full_qualified_name(name, parent_name)
    parts = full_name.split(".")
    return set([".".join(parts[i:]) for i in range(len(parts))])
