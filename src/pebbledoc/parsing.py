"""
Tools for parsing rst into GitHub-flavored Markdown.

This module provides functions that parse rst docstrings into Github-flavored
Markdown using the docutils parser. The most important member of the module is
the :func:`parse_docstring` function. It takes a docstring and parses it into
an equivalent Markdown string.
"""

import copy
import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Literal, NotRequired, TypedDict, assert_never

from docutils import core, nodes
from docutils.nodes import subscript

from . import util
from .config import PebbledocConfig
from .directives import VersionNotice
from .roles import SphinxRef

_admonitions_map = {
    "attention": "important",
    "danger": "caution",
    "error": "caution",
    "hint": "tip",
    "seealso": "note",
    "admonition": "note",
}


class ParameterFieldDict(TypedDict):
    """Dictionary for parameter field list items."""

    body_text: NotRequired[str]
    type_hint: NotRequired[str]


class MixedFieldListError(Exception):
    """
    Raised when a field list contains mixed fields.

    Fields are considered mixed when the field list contains both the
    Sphinx-specific parameter field list names ``param``, ``return``,
    ``returns``, ``raise``, or ``raises``, while also containing other,
    non-specific fields.
    """

    pass


@dataclass
class ListContext:
    """
    Context node for traversal of lists in the rst doctree.

    Converting lists (both bullet lists and enumerated lists) requires
    knowledge about both the width of the enumerating item (a dash or a
    number of various width), and the nesting level. The visitor pattern
    typically keeps no memory of previously visited items, so it is in
    itself not able to accurately parse lists by just pre- and appending
    characters.

    To provide the necessary information to the visitor, it builds a
    stack of previously visited list blocks. Instances of this class
    provide a convenient wrapper around all relevant information about
    each visited list block.
    """

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


def _format_as_quote(text: str) -> str:
    """
    Format the text as a block quote, by prefixing every line with a ``>``.

    :param text: Arbitrary text to format as block quote. Should already
        be in rst format.
    :return: The ``text`` formatted as a block quote.
    """
    text = text.removesuffix("\n")
    text = re.sub(r"(.+\n)", r"> \1", text)
    text = re.sub(r"\n\n", r"\n>\n", text)
    return text


def _parse_multiple_nodes(
    children: Iterable[nodes.Node],
    config: PebbledocConfig,
    document: nodes.document,
    valid_targets: set[str] | None = None,
    current_block_context: str | None = None,
    current_list_context: list[ListContext] | None = None,
) -> str:
    """
    Parse an iterable of nodes into Markdown format.

    :param children: An iterable of doctree nodes that should be parsed
        into Markdown.
    :param config: The pebbledoc's configuration object for how to parse
        the nodes.
    :param document: The document to use for the visitor object.
    :param valid_targets: The set of valid targets for the new visitor.
    :param current_block_context: A context to add to the block content
        of the new visitor. This is useful to set the block context when
        the children nodes appear inside a context that is not a simple
        paragraph and therefore need to be formatted differently.
    :param current_list_context: The current list context. This is useful
        to ensure that lists inside the children nodes are rendered
        correctly when they are already nested inside a list. It is best
        to pass a copy of the original visitors list context, as this
        context will be altered.
    :return: The nodes parsed as Markdown.
    """
    sub_visitor = SphinxRstVisitor(config, document, valid_targets)
    if current_block_context is not None:
        sub_visitor.block_context.append(current_block_context)
    if current_list_context is not None:
        sub_visitor.list_context = current_list_context
    for child in children:
        child.walkabout(sub_visitor)
    return sub_visitor.astext()


def _render_admonition(
    admonition_type: str,
    admonition_node: nodes.Element,
    config: PebbledocConfig,
    document: nodes.document,
    valid_targets: set[str] | None = None,
) -> str:
    """
    Render the given ``admonition_node`` as a Markdown admonition.

    The function takes into account the admonition strategy from the
    config object to format the given admonition node of the given title
    into a Github-flavored Markdown admonition.

    :param admonition_type: The name of the admonition type (e.g. ``note``,
        ``attention``, ``warning``, etc.).
    :param admonition_node: The doctree element node of the admonition.
        Must have the content of the admonition as children.
    :param config: The pebbledoc's configuration object for how to parse
        the admonition.
    :param document: The document to use for the visitor object.
    :param valid_targets: The set of valid targets for the visitor.
    :return: The admonition, parsed as a valid Github-flavored Markdown
        admonition.
    """
    strategy = config.admonition_style

    # handle custom titles
    title = None
    title_node = admonition_node.next_node(nodes.title)
    if title_node is not None:
        if strategy != "map":  # in map mode, titles are overridden
            title = title_node.astext()
        admonition_node.remove(title_node)  # avoid rendering twice

    # handle cases for unsupported strategies
    unsupported = admonition_type in _admonitions_map.keys()
    if strategy == "mix":
        strategy = "classic" if unsupported else "github"
    if strategy == "map":
        strategy = "github"
        if unsupported:
            admonition_type = _admonitions_map[admonition_type]

    # find the correct header
    header_title = title or admonition_type
    if strategy == "github":
        header = f"[!{header_title.upper()}]"
    elif strategy == "classic":
        header = f"**{header_title.capitalize()}:**"
    else:
        assert_never(strategy)

    # remove Sphinx-specific :collapsible: option

    # find body and construct admonition
    body = _parse_multiple_nodes(
        admonition_node.children, config, document, valid_targets
    )
    admonition = _format_as_quote(f"{header}\n\n{body}")
    return admonition + "\n"


class SphinxRstVisitor(nodes.SparseNodeVisitor):
    def __init__(
        self,
        config: PebbledocConfig,
        document: nodes.document,
        valid_targets: set[str] | None = None,
    ) -> None:
        super().__init__(document)
        self.config: PebbledocConfig = config
        self.valid_targets = valid_targets
        self.body: list[str] = []
        self.block_context: list[str] = ["paragraph"]  # visited block type
        self.list_context: list[ListContext] = []  # list nesting level

    def astext(self) -> str:
        """
        After traversal, return the parsed document as a string.

        The method takes the collected pieces of the document from visitor
        traversal of a doctree and concatenates them into a single string.

        :return: The parsed document as a string in Github-flavored
            Markdown format.
        """
        return "".join(self.body)

    def _is_valid_target(self, target: str) -> bool:
        """
        Return True if the target is valid according to ``self.valid_targets``.

        Given the full name of a Sphinx-style reference role, as the
        reference node provides it (i.e. stripped of leading ``~`` and
        ``!``, but otherwise still not normalized for Markdown), check
        whether it is in the list of valid targets and return the result
        as boolean. If no set of valid targets was provided, this method
        always returns True.

        :param target: The full name of a reference target for a
            Sphinx-style reference role, as a string.
        :return: Boolean, describing whether the target is in the set of
            valid targets.
        """
        if self.valid_targets is None:
            return True
        return target in self.valid_targets

    def _create_parameter_list(
        self,
        parameters: dict[str, ParameterFieldDict],
        raises: list[str],
        returns: ParameterFieldDict,
    ) -> None:
        """
        Return a formatted list of function parameters.

        Given the data for parameters, exceptions raised, and the return
        data of a function as extracted from the docstring, this method
        creates a Markdown-formatted list of these parameters.

        The data input must be of the following format:

        - ``parameters``: A dictionary, mapping parameter names to
          dictionaries of type ``ParameterFieldDict``. These are
          dictionaries containing the keys ``body_text`` and ``type_hint``
          containing the description and type description of the parameter.
        - ``raises``: A list of the exceptions raised by the function,
          already formatted as bullet points.
        - ``returns``: A ``ParameterFieldDict`` that contains the
          description and type description of the returned value.

        The resulting list is automatically added to the body of the
        visitor.

        :param parameters: A dictionary mapping parameter names to
            ``ParameterFieldDict``s, containing their description.
        :param raises: A list of bullet points, describing the exceptions
            raised.
        :param returns: A single ``ParameterFieldDict`` that contains
            the description and type description of the returned value.
        :return: None, formatted list is added to text body.
        """
        if parameters:
            self.body.append("**Parameters:**\n\n")
            for param_name, param_data in parameters.items():
                param_type = param_data["type_hint"]
                type_hint = f" (`{param_type}`)" if param_type else ""
                param_descr = param_data["body_text"]
                descr = f": {param_descr}" if param_descr else "\n"
                self.body.append(f"- `{param_name}`{type_hint}{descr}")
            self.body.append("\n")
        if raises:
            self.body.append("**Raises:**\n\n")
            self.body.append("".join(raises))
            self.body.append("\n")
        if returns["type_hint"] or returns["body_text"]:
            self.body.append("**Returns:**\n\n")
            return_type = returns["type_hint"]
            type_hint = f"`{return_type}`" if return_type else ""
            return_descr = returns["body_text"]
            descr = return_descr if return_descr else "\n"
            colon = ": " if type_hint and return_descr else ""
            self.body.append(f"{type_hint}{colon}{descr}\n")

    # Below follow the node visitation methods that are required to match
    # the minimum specs of pebbledoc, i.e. the most common rst features
    # one encounters in docstrings.

    # INLINE MARKUP
    def visit_paragraph(self, node: nodes.paragraph) -> None:
        pass

    def depart_paragraph(self, node: nodes.paragraph) -> None:
        current_block = self.block_context[-1]
        if current_block == "paragraph":
            self.body.append("\n\n")
        else:
            self.body.append("\n")

    def visit_Text(self, node: nodes.Text) -> None:
        text = node.astext()
        # remove stylistic line breaks (e.g. wrapped lines) from field lists
        if self.block_context[-1] == "field_list":
            text = text.replace("\n", " ")
        self.body.append(text)

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

    def visit_transition(self, node: nodes.transition) -> None:
        self.body.append("<hr />\n\n")

    def visit_title_reference(self, node: nodes.title_reference) -> None:
        self.body.append("`")  # interpreted text treated as literal

    def depart_title_reference(self, node: nodes.title_reference) -> None:
        self.body.append("`")

    def visit_subscript(self, node: subscript) -> Any:
        self.body.append("<sub>")

    def depart_subscript(self, node: subscript) -> Any:
        self.body.append("</sub>")

    def visit_superscript(self, node: nodes.superscript) -> Any:
        self.body.append("<sup>")

    def depart_superscript(self, node: nodes.superscript) -> Any:
        self.body.append("</sup>")

    # DIRECTIVES
    def visit_math_block(self, node: nodes.math_block) -> None:
        self.body.append("```math\n")

    def depart_math_block(self, node: nodes.math_block) -> None:
        self.body.append("\n```\n\n")

    def visit_reference(self, node: nodes.reference) -> None:
        hyperlink = node.get("refuri", None)
        reference = node.get("refid", None)
        name = node.get("name", None)
        target = hyperlink if hyperlink else f"#{reference}"
        if target is None:
            target = "#"  # link with no target
        if name is None:
            self.body.append(target)
            raise nodes.SkipNode
        self.body.append(f"[{name}]({target})")
        raise nodes.SkipNode  # skip duplicating link name

    def visit_target(self, node: nodes.target) -> None:
        ref_id = node.get("refid", None)
        if ref_id is not None:  # render only internal targets
            self.body.append(f'<a name="{ref_id}"></a>\n')

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

    def visit_block_quote(self, node: nodes.block_quote) -> None:
        attribution = node.next_node(nodes.attribution)
        children = [
            c for c in node.children if not isinstance(c, nodes.attribution)
        ]

        # walk children to parse their content
        quote = _parse_multiple_nodes(
            children, self.config, self.document, self.valid_targets
        )
        # replace line beginnings with carets:
        quote = _format_as_quote(quote)

        # render attribution if present
        if attribution is not None:
            quote += f">\n> -- {attribution.astext()}\n\n"
        else:
            quote += "\n"

        self.body.append(quote)
        raise nodes.SkipNode

    def visit_comment(self, node: nodes.comment) -> None:
        self.body.append("<!-- ")

    def depart_comment(self, node: nodes.comment) -> None:
        self.body.append(" -->\n\n")

    # LISTS AND ENUMERATIONS
    def visit_bullet_list(self, node: nodes.bullet_list) -> None:
        self.block_context.append("bullet_list")
        self.list_context.append(ListContext("bullet"))

    def depart_bullet_list(self, node: nodes.bullet_list) -> None:
        self.list_context.pop()
        self.block_context.pop()
        if not self.list_context:
            self.body.append("\n")

    def visit_enumerated_list(self, node: nodes.enumerated_list) -> None:
        self.block_context.append("enumerated_list")
        start = node.get("start", 1)
        self.list_context.append(ListContext("enum", start))

    def depart_enumerated_list(self, node: nodes.enumerated_list) -> None:
        self.list_context.pop()
        self.block_context.pop()
        if not self.list_context:
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
    def visit_attention(self, node: nodes.attention) -> None:
        admonition = _render_admonition(
            "attention", node, self.config, self.document, self.valid_targets
        )
        self.body.append(admonition)
        raise nodes.SkipNode

    def visit_caution(self, node: nodes.caution) -> None:
        admonition = _render_admonition(
            "caution", node, self.config, self.document, self.valid_targets
        )
        self.body.append(admonition)
        raise nodes.SkipNode

    def visit_danger(self, node: nodes.danger) -> None:
        admonition = _render_admonition(
            "danger", node, self.config, self.document, self.valid_targets
        )
        self.body.append(admonition)
        raise nodes.SkipNode

    def visit_error(self, node: nodes.error) -> None:
        admonition = _render_admonition(
            "error", node, self.config, self.document, self.valid_targets
        )
        self.body.append(admonition)
        raise nodes.SkipNode

    def visit_hint(self, node: nodes.hint) -> None:
        admonition = _render_admonition(
            "hint", node, self.config, self.document, self.valid_targets
        )
        self.body.append(admonition)
        raise nodes.SkipNode

    def visit_important(self, node: nodes.important) -> None:
        admonition = _render_admonition(
            "important", node, self.config, self.document, self.valid_targets
        )
        self.body.append(admonition)
        raise nodes.SkipNode

    def visit_note(self, node: nodes.note) -> None:
        admonition = _render_admonition(
            "note", node, self.config, self.document, self.valid_targets
        )
        self.body.append(admonition)
        raise nodes.SkipNode

    def visit_tip(self, node: nodes.tip) -> None:
        admonition = _render_admonition(
            "tip", node, self.config, self.document, self.valid_targets
        )
        self.body.append(admonition)
        raise nodes.SkipNode

    def visit_warning(self, node: nodes.warning) -> None:
        admonition = _render_admonition(
            "warning", node, self.config, self.document, self.valid_targets
        )
        self.body.append(admonition)
        raise nodes.SkipNode

    def visit_admonition(self, node: nodes.admonition) -> None:
        admonition = _render_admonition(
            "admonition", node, self.config, self.document, self.valid_targets
        )
        self.body.append(admonition)
        raise nodes.SkipNode

    # CUSTOM NODES
    def visit_SphinxRef(self, node: SphinxRef) -> None:
        target = node.get("target", "")
        # Perform checks that still need the old target format:
        includes_private = any([x.startswith("_") for x in target.split(".")])
        is_valid_target = self._is_valid_target(target)
        # Turn into a valid GitHub refernce target: We interpret these
        # roles as references to headers containing only the member name
        # itself, not the full reference, so we normalize accordingly:
        target = util.name_to_ref(target)
        display_name = node.astext()
        # render only valid targets
        if target and is_valid_target and not includes_private:
            self.body.append(f"[`{display_name}`](#{target})")
        else:
            self.body.append(f"`{display_name}`")
        raise nodes.SkipNode

    def visit_VersionNotice(self, node: VersionNotice) -> None:
        version_labels = {
            "versionadded": ":heavy_plus_sign: Added in version",
            "version-added": ":heavy_plus_sign: Added in version",
            "versionchanged": ":recycle: Changed in version",
            "version-changed": ":recycle: Changed in version",
            "version-deprecated": ":warning: Deprecated since version",
            "deprecated": ":warning: Deprecated since version",
            "versionremoved": ":x: Removed in version",
            "version-removed": ":x: Removed in version",
        }

        kind = node.get("type")
        version = node.get("version")
        if kind is None or kind not in version_labels.keys():
            raise ValueError(f"Unsupported version notice type: {kind}")
        if version is None:
            raise AttributeError(
                f"Version notice has no version attribute: {node.pformat()}"
            )

        if len(node.children) > 0:
            content = _parse_multiple_nodes(
                node.children, self.config, self.document, self.valid_targets
            )
            body_str = f": {content}"
        else:
            body_str = "\n\n"  # no paragraph node, must add manually

        self.body.append(f"> {version_labels[kind]} {version}{body_str}")
        raise nodes.SkipNode

    # FIELD LISTS
    def visit_field_list(self, node: nodes.field_list) -> None:
        # since we render field lists as bullet lists, we need to add a
        # corresponding list context element to the stack:
        self.list_context.append(ListContext("bullet"))
        self.block_context.append("field_list")
        parameters: dict[str, ParameterFieldDict] = {}
        raises = []
        returns: ParameterFieldDict = {"body_text": "", "type_hint": ""}
        normal_fields = []

        for field_node in node.findall(nodes.field):
            name_node = field_node.next_node(nodes.field_name)
            body_node = field_node.next_node(nodes.field_body)

            # should never happen, but the type system technically allows it:
            if name_node is None:
                raise AttributeError(
                    f"Field node missing field name: {field_node.pformat()}"
                )

            field_name = name_node.astext()
            name_parts = field_name.split(maxsplit=1)
            kind = name_parts[0]
            arg_name = name_parts[1] if len(name_parts) > 1 else ""

            # parse body text as regular rst, if one exists
            if body_node is None:
                body_str = ""
            else:
                body_str = _parse_multiple_nodes(
                    body_node.children,
                    self.config,
                    self.document,
                    self.valid_targets,
                    current_block_context="field_list",
                    current_list_context=copy.copy(self.list_context),
                )
            # Nodes with body have the body as a paragraph node and as such
            # end on a line break. We implicitly rely on this later, so we
            # must add a line break for empty bodies here as well:
            if not body_str:
                body_str = "\n"

            # cover known cases
            if kind == "param":
                parameters.setdefault(
                    arg_name, {"body_text": "", "type_hint": ""}
                )
                parameters[arg_name]["body_text"] = body_str
            elif kind == "type":
                parameters.setdefault(
                    arg_name, {"body_text": "", "type_hint": ""}
                )
                parameters[arg_name]["type_hint"] = body_str.removesuffix("\n")
            elif kind in ["raise", "raises"]:
                identifier = f"`{arg_name}`: " if arg_name else ""
                raises.append(f"- {identifier}{body_str}")
            elif kind in ["return", "returns"]:
                returns["body_text"] += body_str
            elif kind == "rtype":
                returns["type_hint"] = body_str.removesuffix("\n")
            else:
                # normal field list
                normal_fields.append(f"- **{field_name}:** {body_str}")

        # prevent mixing of parameter field lists and normal field lists
        is_param_list = any(
            [parameters, raises, returns["body_text"], returns["type_hint"]]
        )
        if normal_fields and is_param_list:
            raise MixedFieldListError(
                f"Parameter field list contained unsupported fields: \n{normal_fields}"
            )

        # otherwise, handle field lists
        if normal_fields:
            self.body.append("".join(normal_fields))
            self.body.append("\n")
            raise nodes.SkipChildren

        # format parameter lists
        self._create_parameter_list(parameters, raises, returns)
        raise nodes.SkipChildren

    def depart_field_list(self, node: nodes.field_list) -> None:
        self.block_context.pop()
        self.list_context.pop()

    # EXCEPTIONAL NODES
    def visit_system_message(self, node: nodes.system_message) -> None:
        raise nodes.SkipNode


def parse_docstring(
    docstring: str,
    config: PebbledocConfig,
    valid_reference_targets: set[str] | None = None,
) -> str:
    """
    Parse rst docstring to Github-flavored Markdown string.

    .. note::

        The returned string always ends on an empty line, i.e. the last
        character is always a single line break. Even when the last node
        of the doctree for the docstring is a paragraph, and paragraphs
        are rendered with a double line break at the end, this double
        line break is normalized away into a single empty line.

    :param docstring: Docstring of the member to parse, already normalized
        using ``inspect.cleandoc()``.
    :param config: PebbledocConfig object instantiated with the user-specified
        configuration for parsing.
     :param valid_reference_targets: A set of valid target names for
        Sphinx-style reference roles. When given, all references pointing
        to targets that are not in this set will be rendered as plain
        inline literals instead of links. When set to None, all
        references will be rendered as links, even if they end up leading
        to invalid targets. Defaults to None.
    :return: The same docstring, but formatted as Github-flavored Markdown.
    """
    settings = {
        "report_level": 5,
        "halt_level": 5,
        "file_insertion_enabled": False,
        "raw_enabled": False,
    }
    doctree = core.publish_doctree(docstring, settings_overrides=settings)
    visitor = SphinxRstVisitor(config, doctree, valid_reference_targets)
    doctree.walkabout(visitor)
    md_text = visitor.astext().removesuffix("\n\n")
    return md_text + "\n"
