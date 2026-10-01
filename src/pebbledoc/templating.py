"""Functions to enable template parsing."""

from __future__ import annotations

import dataclasses
import re
from pathlib import Path
from typing import Any

import yaml

_INSERTION_DIRECTIVE_RE = re.compile(
    r"^:::[ \t]+(?P<identifier>\S+)[ \t]*\n(?P<body>(?:(?:[ \t]+.*)?\n)*)",
    re.MULTILINE,
)


@dataclasses.dataclass
class InsertionDirective:
    """
    A class used to gather all information about a template directive.

    This class gathers the necessary information to turn a Markdown
    auto-documentation directive into an actual documentation string and
    insert that string at the correct position.
    """

    start: int  # index where directive starts
    end: int  # index where directive ends
    options: dict[str, Any]  # options dictionary
    member_name: str  # fully qualified name of the member to insert


def parse_template(template: Path) -> list[InsertionDirective]:
    """
    Parse the given template file for directives.

    The function reads the given template file in search of insertion
    directives. Every insertion directive is found and parsed into a
    :class:`InsertionDirective` object, holding all relevant information
    on the directive.

    :param template: Path to the template file.
    :return: A list of :class:`InsertionDirective` objects, filled with
        information on all insertion directives discovered in ``template``.
    """
    template = template.resolve()
    if not template.exists() or not template.is_file():
        raise FileNotFoundError(f"Template file {template} not found.")

    content = template.read_text(encoding="utf-8")
    directives = []
    for match in _INSERTION_DIRECTIVE_RE.finditer(content):
        full_name = match.group("identifier")
        body = match.group("body")
        config = yaml.safe_load(body) if body.strip() else {}
        options = config.get("options", {})
        directives.append(
            InsertionDirective(match.start(), match.end(), options, full_name)
        )
    return directives


def replace_template_directives(
    template: Path,
    directives: list[InsertionDirective],
    replacements: dict[str, str],
) -> str:
    """
    Build a new documentation from a template and replacement information.

    Given a template file, a list of :class:`InsertionDirective` objects,
    filled with information about insertion directives discovered in the
    template, and a mapping of directive names to the strings that will
    replace them, this function builds a new documentation string. It
    returns this string.

    :param template: Path to the template file.
    :param directives: List of :class:`InsertionDirective` objects with
        information on insertion directives discovered in the template.
    :param replacements: A mapping of member names to replacements for
        the directive for that member name.
    :return: The template with the insertion directives replaced.
    """
    text = template.read_text(encoding="utf-8")

    # start from back so indices stay accurate during replacement
    for directive in sorted(directives, key=lambda d: d.start, reverse=True):
        if directive.member_name not in replacements:
            doc = (
                "> :bangbang: *TEMPLATE ERROR:* Failed to insert documentation "
                f"for member {directive.member_name}."
            )
        else:
            doc = replacements[directive.member_name]

        text = text[: directive.start] + doc + text[directive.end :]

    return text
