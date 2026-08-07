"""
Module to help register directives not natively understood by docutils.

Sphinx-style docstrings allow directives that docutils does not natively
support, specifically the version notice directives such as
``.. versionadded::``. This module provides a function to register these
roles.
"""

from docutils import nodes
from docutils.parsers.rst import Directive, directives


class VersionNotice(nodes.Admonition, nodes.Element):
    """
    Node for Sphinx-style version notices.
    """

    pass


class SphinxVersionNoticeDirective(Directive):
    """
    Directive for Sphinx-style version notices.

    The directive automatically receives input and creates a
    :class:`VersionNotice` node filled with the relevant information from
    the parsed directive.

    See the docs of ``docutils.parsers.rst.Directive`` for more details.
    """

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True

    def run(self):
        node = VersionNotice()
        node["type"] = self.name
        node["version"] = self.arguments[0]
        if self.content:
            self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


def register_sphinx_version_notice_directives() -> None:
    """
    Register all supported version notice directives.

    :return: None.
    """
    version_notice_directives = [
        "version-added",
        "versionadded",
        "version-changed",
        "versionchanged",
        "version-removed",
        "versionremoved",
        "version-deprecated",
        "deprecated",
    ]
    for directive in version_notice_directives:
        directives.register_directive(directive, SphinxVersionNoticeDirective)
