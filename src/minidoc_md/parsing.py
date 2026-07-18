"""
Tools for parsing rst into GitHub-flavored Markdown.

This module provides functions that parse rst docstrings into Github-flavored
Markdown using the docutils parser. The most important member of the module is
the :func:`parse_docstring` function. It takes a docstring and parses it into
an equivalent Markdown string.
"""

from dataclasses import dataclass
from typing import Literal, assert_never

from docutils import core, nodes

from .config import MinidocConfig

_admonitions_map = {
    "attention": "important",
    "danger": "caution",
    "error": "caution",
    "hint": "tip",
    "seealso": "note",
}


@dataclass
class ListContext:
    list_type: Literal["bullet", "enum"]
    counter: int = 1
    marker_width: int = 0

    def __post_init__(self) -> None:
        """Automatically determine initial marker width."""
        if self.list_type == "bullet":
            self.marker_width = 2
        elif self.list_type == "enum":
            self.marker_width = 3
        else:
            raise ValueError(f"Invalid list_type: {self.list_type}")


class SphinxRstVisitor(nodes.SparseNodeVisitor):
    def __init__(self, config: MinidocConfig, document: nodes.document) -> None:
        super().__init__(document)
        self.config: MinidocConfig = config
        self.body: list[str] = []
        self.current_block: str = "paragraph"  # visited block type
        self.list_context: list[ListContext] = []

    # Below follow the node visitation methods that are required to match
    # the minimum specs of minidoc-md, i.e. the most common rst features
    # one encounters in docstrings.

    # INLINE MARKUP
    def visit_paragraph(self, node: nodes.paragraph) -> None:
        pass

    def depart_paragraph(self, node: nodes.paragraph) -> None:
        if self.current_block == "paragraph":
            self.body.append("\n\n")
        else:
            self.body.append("\n")

    def visit_Text(self, node: nodes.Text) -> None:
        self.body.append(node.astext())

    def visit_emphasis(self, node: nodes.emphasis) -> None:
        self.body.append("*")

    def depart_emphasis(self, node: nodes.emphasis) -> None:
        self.body.append("*")

    def visit_strong(self, node: nodes.strong) -> None:
        self.body.append("**")

    def depart_strong(self, node: nodes.strong) -> None:
        self.body.append("**")

    def visit_math(self, node: nodes.math) -> None:
        self.body.append("$")

    def depart_math(self, node: nodes.math) -> None:
        self.body.append("$")

    def visit_literal(self, node: nodes.literal) -> None:
        self.body.append("`")

    def depart_literal(self, node: nodes.literal) -> None:
        self.body.append("`")

    # DIRECTIVES
    def visit_math_block(self, node: nodes.math_block) -> None:
        self.body.append("$$\n")

    def depart_math_block(self, node: nodes.math_block) -> None:
        self.body.append("\n$$\n\n")

    # BLOCKS
    def visit_literal_block(self, node: nodes.literal_block) -> None:
        classes = node["classes"]
        if "code" in classes:
            classes.remove("code")
        if len(classes) > 0:
            language = classes[0]
        else:
            language = ""  # keep language unspecified
        self.body.append(f"```{language}\n")

    def depart_literal_block(self, node: nodes.literal_block) -> None:
        self.body.append("\n```\n\n")

    def visit_doctest_block(self, node: nodes.doctest_block) -> None:
        self.body.append("```doctest\n")

    def depart_doctest_block(self, node: nodes.doctest_block) -> None:
        self.body.append("\n```\n\n")

    # LISTS AND ENUMERATIONS
    def visit_bullet_list(self, node: nodes.bullet_list) -> None:
        self.current_block = "bullet_list"
        self.list_context.append(ListContext("bullet"))

    def depart_bullet_list(self, node: nodes.bullet_list) -> None:
        self.list_context.pop()
        if not self.list_context:
            self.current_block = "paragraph"
            self.body.append("\n")

    def visit_enumerated_list(self, node: nodes.enumerated_list) -> None:
        self.current_block = "enumerated_list"
        start = node.get("start", 1)
        self.list_context.append(ListContext("enum", start))

    def depart_enumerated_list(self, node: nodes.enumerated_list) -> None:
        self.list_context.pop()
        if not self.list_context:
            self.current_block = "paragraph"
            self.body.append("\n")

    def visit_list_item(self, node: nodes.list_item) -> None:
        context = self.list_context[-1]
        prev_indents = (ctx.marker_width for ctx in self.list_context[:-1])
        indent = sum(prev_indents) * " "
        if context.list_type == "bullet":
            marker = "- "
        elif context.list_type == "enum":
            marker = f"{context.counter}. "
            # update list context for current item
            context.counter += 1
            context.marker_width = len(marker)  # update marker width
        else:
            assert_never(context.list_type)
        self.body.append(f"{indent}{marker}")

    # ADMONITIONS

    # EXCEPTIONAL NODES
    def visit_system_message(self, node: nodes.system_message) -> None:
        raise nodes.SkipNode

    def astext(self) -> str:
        """
        After traversal, return the parsed document as a string.

        The method takes the collected pieces of the document from visitor
        traversal of a doctree and concatenates them into a single string.

        :return: The parsed document as a string in Github-flavored
            Markdown format.
        """
        return "".join(self.body)


def parse_docstring(docstring: str, config: MinidocConfig) -> str:
    """
    Parse rst docstring to Github-flavored Markdown string.

    :param docstring: Docstring of the member to parse, already normalized
        using ``inspect.cleandoc()``.
    :param config: MinidocConfig object instantiated with the user-specified
        configuration for parsing.
    :return: The same docstring, but formatted as Github-flavored Markdown.
    """
    settings = {
        "report_level": 5,
        "halt_level": 5,
        "file_insertion_enabled": False,
        "raw_enabled": False,
    }
    doctree = core.publish_doctree(docstring, settings_overrides=settings)
    # dump(doctree)
    # print("\n")
    # print(doctree.pformat())
    visitor = SphinxRstVisitor(config, doctree)
    doctree.walkabout(visitor)
    return visitor.astext()


def dump(node, indent=0):
    print(" " * indent, type(node).__name__)

    for child in node.children:
        dump(child, indent + 2)
