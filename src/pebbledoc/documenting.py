"""Utilities for turning member trees into documentation."""

from __future__ import annotations

from . import parsing, util
from .config import PebbledocConfig
from .inspect_runtime import Member, build_member_tree


def markdown_documentation(
    package_name: str,
    config: PebbledocConfig,
) -> str:
    """
    Create a documentation for the package of the given name.

    The function imports the package of name ``package_name`` and finds
    its public API. It does this by looking for a defined ``__all__``
    in the top-level of the package. If none is found, it instead attempts
    to discover all public members. Sub-packages and sub-modules are
    discovered recursively as well.

    The function then retrieves the docstring of every member and from
    them builds a full API documentation, formatted as GitHub-flavored
    Markdown. The resulting string is returned.

    :param package_name: The name of the package as it should appear in
        the header of the document.
    :param package_obj: The package to document as a Python object,
        retrieved for example using ``importlib.import_module``.
    :param config: A filled pebbledoc config object, detailing how to
        parse the found docstrings and how to arrange them into the final
        document.
    :return: A full API document for the package, formatted as GitHub-
        flavored Markdown, ready for use as a single-file documentation
        or insertion into a template.
    """
    # Build header
    if config.document_title:
        header = f"# {config.document_title}\n\n"
    else:
        header = f"# {package_name} documentation\n\n"

    root = build_member_tree(package_name, config)
    valid_targets = _valid_reference_targets(root)
    main_body = _document_member(root, config, valid_targets)

    # TODO: build an introductory paragraph

    # build TOC
    if config.include_toc:
        toc = "#### Table of contents\n"
        toc += _build_toc(root, config)
        toc += "\n\n"
    else:
        toc = ""

    return f"{header}{toc}{main_body}"


def _build_toc(root: Member, config: PebbledocConfig) -> str:
    """
    Build a table of contents from the root member node of a package.

    Given a root member node, assembled with for example
    :func:`_member_module`, this function builds a table of contents with
    links to the names of all members, and returns it as string. The
    function will only create the list of sections, not the TOC header.

    .. important::

        To determine when a given node is the root node of a package
        which we aim to document, the ``config`` object **must** have
        its ``package_name`` attribute filled with the correct name.
        Otherwise, the ``no_main_module_header`` option will not be
        respected.

    :param root: The root :class:`Member` node of a package for which to
        build a table of contents.
    :param config: The pebbledoc config object.
    :return: A nested list of links, pointing to the header of the section
        for each of the children of ``root``.
    """
    # find out if we are handling the top-level node
    is_pkg_root = root.name == config.package_name
    toc = ""
    full_name = util.full_qualified_name(root.name, root.parent)
    if not is_pkg_root or config.main_module_header:
        toc = f"- [`{full_name}`](#{util.name_to_ref(full_name)})\n"
    # iteratively add children, descending into submodules
    for child in root.children:
        full_name = util.full_qualified_name(child.name, child.parent)
        if child.kind == "module":
            toc += _build_toc(child, config)  # descend into submodules
        else:
            ref_target = util.name_to_ref(full_name)
            spacer = (
                "" if is_pkg_root and not config.main_module_header else "  "
            )
            toc += f"{spacer}- [`{full_name}`](#{ref_target})\n"
    return toc


def _valid_reference_targets(member: Member) -> set[str]:
    """
    Return a set of valid targets for the member and its children.

    Given a :class:`Member` tree, construct a set of all valid targets
    that these members will create. This includes the full qualified
    name of each member, plus all partial names.

    .. note::

        The set will contain *actual* target names, the way that they
        are written in the Sphinx reference role, i.e. including dots,
        capitalization, etc. To turn them into Markdown references, they
        must be run through the :func:`~util.name_to_ref` function first.

    :param member: Any :class:`Member` instance, possibly including
        children, for which to generate a set of valid target names.
    :return: A set of valid target names, as they would be given by a
        valid Sphinx-style reference role.
    """
    full_name = util.full_qualified_name(member.name, member.parent)
    parts = full_name.split(".")
    valid_targets = set([".".join(parts[i:]) for i in range(len(parts))])
    if member.children:
        for child in member.children:
            valid_targets = valid_targets | _valid_reference_targets(child)
    return valid_targets


def _document_member(
    member: Member,
    config: PebbledocConfig,
    valid_reference_targets: set[str] | None = None,
) -> str:
    """
    Create the documentation section for the given member.

    Function also recursively descends into the members children and
    generates their documentation, and appends it to the member
    documentation.

    :param member: A member node from the member tree constructed by
        :func:`_member_module`.
    :param config: The pebbledoc configuration object.
    :param valid_reference_targets: A set of valid target names for
        Sphinx-style reference roles. When given, all references pointing
        to targets that are not in this set will be rendered as plain
        inline literals instead of links. When set to None, all
        references will be rendered as links, even if they end up leading
        to invalid targets. Defaults to None.
    :return: Documentation section for ``member`` as a string, formatted
        as GitHub-flavored Markdown.
    """
    snippet = ""

    # add a header, unless suppressed
    is_pkg_root = member.name == config.package_name
    exclude_header = is_pkg_root and not config.main_module_header
    if not exclude_header:
        # add an anchor for references without the full name
        full_name = util.full_qualified_name(member.name, member.parent)
        parts = full_name.split(".")
        targets = [".".join(parts[i:]) for i in range(1, len(parts))]
        for target in targets:
            snippet += f'<a name="{util.name_to_ref(target)}"></a>\n'
        snippet += f"{'#' * member.header_level} "
        snippet += f"`{full_name}`\n\n"
        if config.include_back_to_top:
            if config.document_title:
                top_header = util.name_to_ref(config.document_title)
            else:
                top_header = util.name_to_ref(
                    f"{config.package_name} documentation"
                )
            snippet += f"<sup>[Back to top](#{top_header})</sup>\n\n"

    # Add a signature
    if member.signature:
        snippet += f"```Python\n{member.signature}\n```\n\n"

    # Render and add the docstring
    if member.raw_docstring:
        snippet += parsing.parse_docstring(
            member.raw_docstring, config, valid_reference_targets
        )
        snippet += "\n"

    # Recursively render children as well
    if member.children:
        for child in member.children:
            snippet += _document_member(child, config, valid_reference_targets)

    return snippet
