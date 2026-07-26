"""Utilities used in multiple modules."""

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
    target = name.removeprefix("_")  # private methods need to be stripped
    target = re.sub(r"[^a-z0-9\s\-_]", "", target.lower())
    target = target.strip().replace(" ", "-")
    target = target.replace("_", "-")
    return target
