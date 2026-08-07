"""
Module to automatically discover package members and document them.

The module contains the :func:`document_package`, which automatically
discovers all members of a given package and then automatically renders
documentation for it by retrieving docstrings for the members and
ordering them into a structured single-file document, formatted as
GitHub-flavored Markdown.
"""

from __future__ import annotations

import ast
import inspect
from collections.abc import Callable
from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

from . import util
from .config import MinidocConfig
from .parsing import parse_docstring


@dataclass
class Member:
    """Dataclass to represent a documented member of a package."""

    name: str
    parent: str
    kind: str
    signature: str
    raw_docstring: str
    header_level: int
    children: list[Member] = field(default_factory=list)


def _is_local(member: object, package: str) -> bool:
    """
    Whether the given member is defined in the specified package.

    :param member: Any Python object.
    :param package: The name of the package against which to check
        membership.
    :return: True, if the member is defined in the specified package,
        otherwise False.
    """
    if inspect.ismodule(member):
        return getattr(member, "__name__", "").startswith(package)
    elif hasattr(member, "__module__"):
        return getattr(member, "__module__", "").startswith(package)
    # last option: neither a module nor a class/function, probably a const
    return False


def _explicitly_reexported(package: ModuleType) -> list[str]:
    """
    Find all members of a package that were explicitly reexported.

    The function parses the file corresponding to the package into an
    AST tree and extracts all members that were explicitly re-exported.
    This includes all types of members, even from external packages.

    Names marked as private (starting with an underscore) are excluded.

    :param package: The package whose explicitly re-exported members to
        extract. Must be an actual package object, not just the name.
    :return: A list of the names of all members which the package
        explicitly re-exports.
    """
    # attempt to discover origin of the package
    init_file = None
    if package.__spec__ is not None:
        init_file = package.__spec__.origin
    if init_file is None:
        init_file = package.__file__
    if init_file is None:
        raise FileNotFoundError(
            f"Unable to find origin of module {package.__name__}"
        )
    print(init_file)

    # parse the __init__.py (or other origin) of the package as AST
    init_file = Path(init_file).resolve()
    ast_tree = ast.parse(
        init_file.read_text(encoding="utf-8"),
        filename=str(init_file),
    )

    # identify all re-exports and list them, unless private
    explicit_reexports = set()
    for node in ast_tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                explicit_reexports.add(
                    alias.asname or alias.name.split(".", 1)[0]
                )
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                explicit_reexports.add(alias.asname or alias.name)
    return [m for m in explicit_reexports if not m.startswith("_")]


def discover_public_members(module: ModuleType) -> list[str]:
    """
    Discover all public members of a module or package.

    The function prefers ``__all__`` of the module defines it. If it does,
    ``__all__`` is returned as-is. Otherwise, the function finds all
    members in the namespace of the module, including those that were
    imported. Modules that were not explicitly imported fully are not
    included. However, external members from third-party or standard
    library packages will be included as well and must be removed later.

    :param module: The module object for which to discover public members.
    :return: A list of all public members. That is, a list of all members
        not starting with an underscore and importable from the module,
        but excluding those modules and packages that are only available
        because members were imported from them, without being explicitly
        imported themselves.
    """
    # attempt to find explicit API first
    module_all = getattr(module, "__all__", None)
    if module_all is not None:
        return module_all

    # fall back to discovery
    explicitly_reexported = _explicitly_reexported(module)
    public_members = []
    for name, member in vars(module).items():
        if name.startswith("_"):
            # exclude private members
            continue
        if inspect.ismodule(member) and name not in explicitly_reexported:
            # Modules that are only in module.__dict__ because we import
            # something from them, but do not explicitly re-export them
            # themselves do not go into list of public members!
            continue
        public_members.append(name)
    return public_members


def _parent_name(name: str, parent_name: str) -> str:
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


def _signature_str(
    sig: inspect.Signature, is_classmethod: bool = False
) -> str:
    """
    Turn a signature object into a description of itself.

    This is needed to correctly display signatures even when they are
    strings or when ``from __future__ import annotations`` is used.

    :param sig: Signature object to turn into a string description.
    :param is_classmethod: Set to True when the routine is a class
        method. ``inspect.signature`` does not recognize the ``cls``
        parameter of classmethods, as it sees them as normal functions,
        so the parameter must be added manually.
    :return: String description of the signature ``sig``.
    """
    # check what kind of "special" parameters we will find
    param_kinds = [p.kind.description for p in sig.parameters.values()]
    has_pos_only = any([kind == "positional-only" for kind in param_kinds])
    has_kw_only = any([kind == "keyword-only" for kind in param_kinds])
    has_vp = any([kind == "variadic positional" for kind in param_kinds])

    # add signature for each parameter
    params = []
    if is_classmethod:
        params.append("cls")
    for name, param in sig.parameters.items():
        descr = name
        kind = param.kind.description
        if kind == "variadic positional":
            descr = f"*{descr}"
        if kind == "variadic keyword":
            descr = f"**{descr}"
        if kind == "keyword-only" and has_kw_only and not has_vp:
            params.append("*")
            has_kw_only = False  # found transition, can stop looking
        if kind == "positional or keyword" and has_pos_only:
            params.append("/")
            has_pos_only = False  # we've found it, no longer need to look
        if param.annotation is not inspect.Signature.empty:
            descr += f": {param.annotation}"
        if param.default is not inspect.Parameter.empty:
            bracket = "'" if isinstance(param.default, str) else ""
            descr += f" = {bracket}{param.default}{bracket}"
        params.append(descr)

    # add return type annotation, if present
    signature_str = f"({', '.join(params)})"
    return_annotation = sig.return_annotation
    if return_annotation is not inspect.Signature.empty:
        signature_str += f" -> {return_annotation}"
    return signature_str


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
    full_name = _parent_name(member.name, member.parent)
    parts = full_name.split(".")
    valid_targets = set([".".join(parts[i:]) for i in range(len(parts))])
    if member.children:
        for child in member.children:
            valid_targets = valid_targets | _valid_reference_targets(child)
    return valid_targets


def _document_member(
    member: Member,
    config: MinidocConfig,
    valid_reference_targets: set[str] | None = None,
) -> str:
    """
    Create the documentation section for the given member.

    Function also recursively descends into the members children and
    generates their documentation, and appends it to the member
    documentation.

    :param member: A member node from the member tree constructed by
        :func:`_member_module`.
    :param config: The Minidoc configuration object.
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
        full_name = _parent_name(member.name, member.parent)
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
        snippet += parse_docstring(
            member.raw_docstring, config, valid_reference_targets
        )
        snippet += "\n"

    # Recursively render children as well
    if member.children:
        for child in member.children:
            snippet += _document_member(child, config, valid_reference_targets)

    return snippet


def _member_constant(name: str, constant: object, parent: str) -> Member:
    """
    Create a :class:`Member` node for a constant.

    :param name: Name of the constant.
    :param constant: The value of the constant.
    :return: A :class:`Member` node for the constant, filled with all
        relevant data.
    """
    # make sure only string type values have quotes
    quotes = "'" if isinstance(constant, str) else ""
    # do not inherit docstrings from parent classes
    sig = f"{name}: {type(constant).__name__} = {quotes}{constant}{quotes}"
    node = Member(
        name=name,
        parent=parent,
        kind="constant",
        signature=sig,
        raw_docstring="",  # empty for now, retrieval complicated
        header_level=3,
    )
    return node


def _member_function(
    name: str, function: Callable[..., Any], parent: str
) -> Member:
    """
    Create a :class:`Member` node for a function.

    :param name: Name of the function.
    :param function: The function object itself.
    :return: A :class:`Member` node for the function, filled with all
        relevant data.
    """
    sig = _signature_str(inspect.signature(function))
    doc = inspect.getdoc(function) or ""
    node = Member(
        name=name,
        parent=parent,
        kind="routine",
        signature=f"{name}{sig}",
        raw_docstring=doc,
        header_level=3,
    )
    return node


def _member_method(
    name: str,
    method: Callable[..., Any],
    parent: str,
    decorator: str | None = None,
) -> Member:
    """
    Create a :class:`Member` node for a method.

    This function is also used for all decorated methods, especially
    class methods and static methods.

    :param name: Name of the method.
    :param method: The method object itself.
    :param parent: The nameof the parent class.
    :param decorator: The name of the decorator for the method, or None
        if the method has no decorator.
    :return: A :class:`Member` node for the method, filled with all
        relevant data.
    """
    sig = ""
    if decorator:
        sig += f"@{decorator}\n"
    parent_class = parent.split(".")[-1]
    sig += f"{parent_class}.{name}"
    sig += _signature_str(
        inspect.signature(method), decorator == "classmethod"
    )
    doc = inspect.getdoc(method) or ""
    node = Member(
        name=name,
        parent=parent,
        kind="method",
        signature=sig,
        raw_docstring=doc,
        header_level=4,
    )
    return node


def _member_property(name: str, property_: property, parent: str) -> Member:
    """
    Create a :class:`Member` node for a property.

    :param name: Name of the property.
    :param property_: The property object itself.
    :param parent: The name of the parent class.
    :return: A :class:`Member` node for the property, filled with all
        relevant data.
    """
    if property_.fget is None:
        annotation = ": Any"  # TODO: handle more consistently
    else:
        return_annotation = inspect.signature(property_.fget).return_annotation
        if return_annotation is inspect.Parameter.empty:
            annotation = ""
        else:
            annotation = f": {return_annotation}"
    parent_class = parent.split(".")[-1]
    sig = f"@property\n{parent_class}.{name}{annotation}"
    doc = inspect.getdoc(property_) or ""
    node = Member(
        name=name,
        parent=parent,
        kind="property",
        signature=sig,
        raw_docstring=doc,
        header_level=4,
    )
    return node


def _member_classvar(name: str, classvar: object, parent: str) -> Member:
    """
    Create a :class:`Member` node for a class variable.

    :param name: Name of the class variable.
    :param classvar: The value of the class variable.
    :param parent: The name of the parent class.
    :return: A :class:`Member` node for the class, filled with all
        relevant data.
    """
    q = "'" if isinstance(classvar, str) else ""
    parent_class = parent.split(".")[-1]
    sig = (
        f"{parent_class}.{name}: ClassVar[{type(classvar).__name__}] "
        f"= {q}{classvar}{q}"
    )
    node = Member(
        name=name,
        parent=parent,
        kind="classvar",
        signature=sig,
        raw_docstring="",  # empty for now, retrieval complicated
        header_level=4,
    )
    return node


def _member_class(name: str, klass: type, parent: str) -> Member:
    """
    Create a :class:`Member` node for a class.

    It will also automatically create children nodes for all class members.

    :param name: Name of the class.
    :param klass: The class object itself.
    :return: A :class:`Member` node for the class, filled with all
        relevant data.
    """
    parents = ", ".join([c.__name__ for c in klass.__bases__])
    kind = "dataclass" if is_dataclass(klass) else "class"
    sig = ""
    if kind == "dataclass":
        sig += "@dataclass\n"
    sig += f"{name}({parents})"
    doc = inspect.getdoc(klass) or ""

    # find dataclass fields if the class is a dataclass
    if is_dataclass(klass):
        fields_set = {f.name for f in fields(klass)}
    else:
        fields_set = set()

    # find all public members of the class
    class_members = [m for m in klass.__dict__.keys() if not m.startswith("_")]
    children = []
    new_parent = _parent_name(name, parent)
    for child_name in class_members:
        obj = getattr(klass, child_name)
        child_kind = klass.__dict__[child_name]
        if inspect.isroutine(obj):
            if isinstance(child_kind, staticmethod):
                decorator = "staticmethod"
            elif isinstance(child_kind, classmethod):
                decorator = "classmethod"
            elif getattr(child_kind, "__isabstractmethod__", False):
                decorator = "abstractmethod"
            else:
                decorator = None
            children.append(
                _member_method(child_name, obj, new_parent, decorator)
            )
        elif isinstance(child_kind, property):
            children.append(_member_property(child_name, obj, new_parent))
        elif inspect.isclass(obj):
            children.append(_member_class(child_name, obj, new_parent))
        elif child_name in fields_set:
            continue  # we do not document fields with defaults
        else:
            children.append(_member_classvar(child_name, obj, new_parent))

    # construct the node
    node = Member(
        name=name,
        parent=parent,
        kind=kind,
        signature=sig,
        raw_docstring=doc,
        header_level=3,
        children=children,
    )
    return node


def _member_module(
    name: str,
    module: ModuleType,
    config: MinidocConfig,
    library_name: str,
    parent: str = "",
) -> Member:
    """
    Create a :class:`Member` node for a module.

    The function can also be used for a package.

    :param name: Name of the module.
    :param module: The module object itself.
    :param config: The Minidoc config object.
    :param library_name: The top level package under which the current
        module exists, i.e. the name of the project that is being
        documented.
    :param parent: The name of the parent module, or an empty string
        if there is no parent module.
    :return: A :class:`Member` node for the module, filled with all
        relevant data.
    """
    # gather information required for the node
    if config.module_docstring:
        doc = inspect.getdoc(module) or ""
    else:
        doc = ""

    # find all public members of the module
    public_members = discover_public_members(module)

    # find children, create their nodes
    children = []
    sub_modules = []
    new_parent = _parent_name(name, parent)
    for member_name in public_members:
        member = getattr(module, member_name)
        # avoid including external members (unfortunately, re-exported
        # external constants slip past this check - as would modules if
        # we didn't exclude them explicitly)
        is_local = _is_local(member, library_name)
        is_constant = not hasattr(
            member, "__module__"
        ) and not inspect.ismodule(member)
        if not is_local and not is_constant:
            continue  # do not include external members into docs
        if inspect.isfunction(member):
            children.append(_member_function(member_name, member, new_parent))
        elif inspect.isclass(member):
            children.append(_member_class(member_name, member, new_parent))
        elif inspect.ismodule(member):
            sub_modules.append(
                _member_module(
                    member_name, member, config, library_name, new_parent
                )
            )
        else:
            if not config.document_constants:
                continue  # skip constants
            children.append(_member_constant(member_name, member, new_parent))

    # create module member node
    node = Member(
        name=name,
        parent=parent,
        kind="module",
        signature="",  # modules get no signature section
        raw_docstring=doc,
        header_level=2,  # modules always have h2 header
        children=children + sub_modules,  # submodules follow other members
    )
    return node


def _build_toc(root: Member, config: MinidocConfig) -> str:
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
    :param config: The Minidoc config object.
    :return: A nested list of links, pointing to the header of the section
        for each of the children of ``root``.
    """
    # find out if we are handling the top-level node
    is_pkg_root = root.name == config.package_name
    toc = ""
    full_name = _parent_name(root.name, root.parent)
    if not is_pkg_root or config.main_module_header:
        toc = f"> - [`{full_name}`](#{util.name_to_ref(full_name)})\n"
    # iteratively add children, descending into submodules
    for child in root.children:
        full_name = _parent_name(child.name, child.parent)
        if child.kind == "module":
            toc += _build_toc(child, config)  # descend into submodules
        else:
            ref_target = util.name_to_ref(full_name)
            spacer = (
                "" if is_pkg_root and not config.main_module_header else "  "
            )
            toc += f"> {spacer}- [`{full_name}`](#{ref_target})\n"
    return toc


def markdown_documentation(
    package_name: str,
    package_obj: ModuleType,
    config: MinidocConfig,
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
    :param config: A filled Minidoc-MD config object, detailing how to
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

    root = _member_module(package_name, package_obj, config, package_name)
    valid_targets = _valid_reference_targets(root)
    main_body = _document_member(root, config, valid_targets)

    # TODO: build an introductory paragraph

    # build TOC
    if config.include_toc:
        toc = "> #### Table of contents\n"
        toc += _build_toc(root, config)
        toc += "\n\n"
    else:
        toc = ""

    return f"{header}{toc}{main_body}"
