"""
Module to automatically discover package members and document them.

The module contains the :func:`document_package`, which automatically
discovers all members of a given package and then automatically renders
documentation for it by retrieving docstrings for the members and
ordering them into a structured single-file document, formatted as
GitHub-flavored Markdown.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass, field, fields, is_dataclass
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
    params = []
    if is_classmethod:
        params.append("cls")
    for name, param in sig.parameters.items():
        descr = name
        if param.annotation is not inspect.Signature.empty:
            descr += f": {param.annotation}"
        if param.default is not inspect.Parameter.empty:
            descr += f" = {param.default}"
        params.append(descr)

    return f"({', '.join(params)}) -> {sig.return_annotation}"


def _document_member(member: Member, config: MinidocConfig) -> str:
    """
    Create the documentation section for the given member.

    Function also recursively descends into the members children and
    generates their documentation, and appends it to the member
    documentation.

    :param member: A member node from the member tree constructed by
        :func:`_package_tree`.
    :param config: The Minidoc configuration object.
    :return: Documentation section for ``member`` as a string, formatted
        as GitHub-flavored Markdown.
    """
    snippet = ""
    # add an anchor for references without the full name
    full_name = _parent_name(member.name, member.parent)
    parts = full_name.split(".")
    targets = [".".join(parts[i:]) for i in range(1, len(parts))]
    for target in targets:
        snippet += f'<a name="{util.name_to_ref(target)}"></a>\n'
    snippet += f"{'#' * member.header_level} "
    header = _parent_name(member.name, member.parent)
    snippet += f"`{header}`\n\n"
    if member.signature:
        snippet += f"```Python\n{member.signature}\n```\n\n"
    if member.raw_docstring:
        snippet += parse_docstring(member.raw_docstring, config)
        snippet += "\n"
    if member.children:
        for child in member.children:
            snippet += _document_member(child, config)
    return snippet


def _member_constant(name: str, constant: object, parent: str) -> Member:
    """
    Create a :class:`Member` node for a constant.

    :param name: Name of the constant.
    :param constant: The value of the constant.
    :return: A :class:`Member` node for the constant, filled with all
        relevant data.
    """
    # do not inherit docstrings from parent classes
    sig = f"{name}: {type(constant).__name__} = {constant}"
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
    parent_class = parent.split(".")[-1]
    sig = f"{parent_class}.{name}: ClassVar[{type(classvar).__name__}] = {classvar}"
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
    public_members = getattr(module, "__all__", None)
    if public_members is None:
        public_members = [
            m for m in module.__dict__.keys() if not m.startswith("_")
        ]

    # find children, create their nodes
    children = []
    sub_modules = []
    new_parent = _parent_name(name, parent)
    for member_name in public_members:
        member = getattr(module, member_name)
        # avoid including external members (unfortunately, re-exported
        # external constants slip past this check - as would modules if
        # we didn't exclude them explicitly)
        is_local = getattr(member, "__module__", "").startswith(library_name)
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

    :param root: The root :class:`Member` node of a package for which to
        build a table of contents.
    :param config: The Minidoc config object.
    :return: A nested list of links, pointing to the header of the section
        for each of the children of ``root``.
    """
    # First entry for the root node
    full_name = _parent_name(root.name, root.parent)
    toc = f"> - [`{full_name}`](#{util.name_to_ref(full_name)})\n"
    # then iteratively add children, descending into submodules
    for child in root.children:
        full_name = _parent_name(child.name, child.parent)
        if child.kind == "module":
            toc += _build_toc(child, config)  # descend into submodules
        else:
            ref_target = util.name_to_ref(full_name)
            toc += f">   - [`{full_name}`](#{ref_target})\n"
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
    header = f"# {package_name} documentation\n\n"

    root = _member_module(package_name, package_obj, config, package_name)
    main_body = _document_member(root, config)

    # build first paragraph if module provides none
    if not root.raw_docstring:
        intro = (
            f"This document lists the full public API of {package_name}.\n\n"
        )
    else:
        intro = ""

    # build TOC
    if config.include_toc:
        toc = "> #### Table of contents\n"
        toc += _build_toc(root, config)
        toc += "\n\n"
    else:
        toc = ""

    return f"{header}{intro}{toc}{main_body}"
