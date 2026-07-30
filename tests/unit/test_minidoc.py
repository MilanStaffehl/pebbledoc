"""Tests for the minidoc module."""

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from minidoc_md import config, minidoc


@pytest.fixture
def patch_parse_docstring(mocker: MockerFixture) -> Mock:
    """Patch the function to parse docstrings."""
    mock_parse_docstring = mocker.patch(
        "minidoc_md.minidoc.parse_docstring",
        side_effect=lambda d, c: f"{d.rstrip('\n')}\n",
    )
    return mock_parse_docstring


@pytest.fixture
def mock_module() -> ModuleType:
    """Return the test mock package."""
    sys.path.insert(0, str(Path(__file__).parent / "resources"))
    module = importlib.import_module("mock_module")
    return module


def test_document_member_all_fields(patch_parse_docstring: Mock) -> None:
    """Test the function for a member with all fields."""

    test_config = config.MinidocConfig()
    test_docstring = "This is a test docstring."
    test_member = minidoc.Member(
        name="test_member",
        parent="parent",
        kind="test_kind",
        signature="test_member = pytest.mock.Mock()",
        raw_docstring=test_docstring,
        header_level=3,
    )

    output = minidoc._document_member(test_member, test_config)
    expected = (
        '<a name="test_member"></a>\n'
        "### `parent.test_member`\n\n"
        "```Python\n"
        "test_member = pytest.mock.Mock()\n"
        "```\n\n"
        "This is a test docstring.\n\n"
    )
    assert output == expected
    patch_parse_docstring.assert_called_once_with(test_docstring, test_config)


def test_document_member_no_docstring(patch_parse_docstring: Mock) -> None:
    """Test the function for a member with no docstring."""

    test_config = config.MinidocConfig()
    test_member = minidoc.Member(
        name="test_member",
        parent="parent",
        kind="test_kind",
        signature="test_member = pytest.mock.Mock()",
        raw_docstring="",
        header_level=3,
    )

    output = minidoc._document_member(test_member, test_config)
    expected = (
        '<a name="test_member"></a>\n'
        "### `parent.test_member`\n\n```Python\ntest_member = "
        "pytest.mock.Mock()\n```\n\n"
    )
    assert output == expected
    patch_parse_docstring.assert_not_called()


def test_document_member_no_signature(patch_parse_docstring: Mock) -> None:
    """Test the function for a member with no signature."""

    test_config = config.MinidocConfig()
    test_docstring = "This is a test docstring."
    test_member = minidoc.Member(
        name="test_member",
        parent="parent",
        kind="test_kind",
        signature="",
        raw_docstring=test_docstring,
        header_level=3,
    )

    output = minidoc._document_member(test_member, test_config)
    expected = (
        '<a name="test_member"></a>\n'
        "### `parent.test_member`\n\nThis is a test docstring.\n\n"
    )
    assert output == expected
    patch_parse_docstring.assert_called_once_with(test_docstring, test_config)


def test_document_member_header_level(patch_parse_docstring: Mock) -> None:
    """Test the function for a member with various header levels."""

    test_config = config.MinidocConfig()
    test_docstring = "This is a test docstring."
    for lvl in range(1, 4):
        test_member = minidoc.Member(
            name="test_member",
            parent="parent",
            kind="test_kind",
            signature="test_member = pytest.mock.Mock()",
            raw_docstring=test_docstring,
            header_level=lvl,
        )

        output = minidoc._document_member(test_member, test_config)
        header_prefix = "#" * lvl
        expected = (
            '<a name="test_member"></a>\n'
            f"{header_prefix} `parent.test_member`\n\n"
            "```Python\n"
            "test_member = pytest.mock.Mock()\n"
            "```\n\n"
            "This is a test docstring.\n\n"
        )
        assert output == expected
        patch_parse_docstring.assert_called_once_with(
            test_docstring, test_config
        )
        patch_parse_docstring.reset_mock()


def test_document_member_children(patch_parse_docstring: Mock) -> None:
    """Test the function for a member with children."""

    test_config = config.MinidocConfig()
    child_one = minidoc.Member(
        name="child_one",
        parent="parent.test_member",
        kind="test_kind",
        signature="test_member = pytest.mock.Mock()",
        raw_docstring="This is child one's docstring.\n\n",
        header_level=4,
    )
    child_two = minidoc.Member(
        name="child_two",
        parent="parent.test_member",
        kind="test_kind",
        signature="test_member = pytest.mock.Mock()",
        raw_docstring="This is child two's docstring.\n\n",
        header_level=4,
    )
    test_member = minidoc.Member(
        name="test_member",
        parent="parent",
        kind="test_kind",
        signature="test_member = pytest.mock.Mock()",
        raw_docstring="This is a test docstring.",
        header_level=3,
        children=[child_one, child_two],
    )

    output = minidoc._document_member(test_member, test_config)
    expected = (
        '<a name="test_member"></a>\n'
        "### `parent.test_member`\n\n"
        "```Python\n"
        "test_member = pytest.mock.Mock()\n"
        "```\n\n"
        "This is a test docstring.\n\n"
        '<a name="child_one"></a>\n'
        "#### `parent.test_member.child_one`\n\n"
        "```Python\n"
        "test_member = pytest.mock.Mock()\n"
        "```\n\n"
        "This is child one's docstring.\n\n"
        '<a name="child_two"></a>\n'
        "#### `parent.test_member.child_two`\n\n"
        "```Python\n"
        "test_member = pytest.mock.Mock()\n"
        "```\n\n"
        "This is child two's docstring.\n\n"
    )
    assert output == expected
    assert patch_parse_docstring.call_count == 3
    assert patch_parse_docstring.call_args_list[0].args[0] == (
        "This is a test docstring."
    )
    assert patch_parse_docstring.call_args_list[1].args[0] == (
        "This is child one's docstring.\n\n"
    )
    assert patch_parse_docstring.call_args_list[2].args[0] == (
        "This is child two's docstring.\n\n"
    )


# == HELPER FUNCTIONS ==================================================


def check_constant_mock_constant(node: minidoc.Member) -> None:
    """Check node for representing constant "MOCK_CONSTANT"."""
    assert node.name == "MOCK_CONSTANT"
    assert node.parent == "mock_module"
    assert node.kind == "constant"
    assert node.signature == "MOCK_CONSTANT: float = 3.12"
    assert node.raw_docstring == ""  # TODO: retrieve docstring
    assert node.header_level == 3


def check_constant_undocumented(node: minidoc.Member) -> None:
    """Check node for representing constant "UNDOCUMENTED"."""
    assert node.name == "UNDOCUMENTED"
    assert node.parent == "mock_module"
    assert node.kind == "constant"
    assert node.signature == "UNDOCUMENTED: bool = False"
    assert node.raw_docstring == ""  # TODO: retrieve docstring
    assert node.header_level == 3


def check_function_mock_function(node: minidoc.Member) -> None:
    """Check node for representing function "mock_function"."""
    assert node.name == "mock_function"
    assert node.parent == "mock_module"
    assert node.kind == "routine"
    assert node.signature == (
        "mock_function(param_a: int, param_b: str, optional: int | None = None) -> str"
    )
    assert node.raw_docstring == (
        "Mock function docstring.\n\n"
        ":param param_a: Parameter A.\n"
        ":param param_b: Parameter B, which has a description that extends\n"
        "    beyond a single line.\n"
        ":param optional: An optional parameter.\n"
        ":return: A string."
    )
    assert node.header_level == 3


def check_function_function_with_custom_type(node: minidoc.Member) -> None:
    """Check node for representing function "function_with_custom_type"."""
    assert node.name == "function_with_custom_type"
    assert node.parent == "mock_module"
    assert node.kind == "routine"
    assert node.signature == (
        "function_with_custom_type(param: MockClass) -> MockDataclass"
    )
    assert node.raw_docstring == (
        "Function with custom types.\n\n"
        ":param param: A MockClass parameter.\n"
        ":return: A MockDataclass."
    )
    assert node.header_level == 3


def check_method_public_method(node: minidoc.Member) -> None:
    """Check node for representing method "public_method"."""
    assert node.name == "public_method"
    assert node.parent == "mock_module.MockClass"
    assert node.kind == "method"
    assert node.signature == (
        "MockClass.public_method(self, param_c: bool, "
        "optional: str | None = None) -> int"
    )
    assert node.raw_docstring == (
        "Public method docstring.\n\n"
        ":param param_c: Parameter C.\n"
        ":param optional: Optional parameter.\n"
        ":return: An integer."
    )
    assert node.header_level == 4


def check_method_class_method(node: minidoc.Member) -> None:
    """Check node for representing class "class_method"."""
    assert node.name == "class_method"
    assert node.parent == "mock_module.MockClass"
    assert node.kind == "method"
    assert node.signature == (
        "@classmethod\nMockClass.class_method(cls, param: int) -> int"
    )
    assert node.raw_docstring == (
        "Class method docstring.\n\n:param param: A parameter.\n:return: An integer."
    )
    assert node.header_level == 4


def check_method_static_method(node: minidoc.Member) -> None:
    """Check node for representing static method "static_method"."""
    assert node.name == "static_method"
    assert node.parent == "mock_module.MockClass"
    assert node.kind == "method"
    assert node.signature == (
        "@staticmethod\nMockClass.static_method(param: int) -> int"
    )
    assert node.raw_docstring == (
        "Static method docstring.\n\n:param param: A parameter.\n:return: An integer."
    )
    assert node.header_level == 4


def check_classvar_class_var(node: minidoc.Member) -> None:
    """Check node for representing class "class_var"."""
    assert node.name == "class_var"
    assert node.parent == "mock_module.MockClass"
    assert node.kind == "classvar"
    assert node.signature == "MockClass.class_var: ClassVar[int] = 0"
    assert node.raw_docstring == ""
    assert node.header_level == 4


def check_classvar_undocumented(node: minidoc.Member) -> None:
    """Check node for representing class "undocumented"."""
    assert node.name == "undocumented"
    assert node.parent == "mock_module.MockClass"
    assert node.kind == "classvar"
    assert node.signature == "MockClass.undocumented: ClassVar[bool] = False"
    assert node.raw_docstring == ""
    assert node.header_level == 4


def check_property_property_editable(node: minidoc.Member) -> None:
    """Check node for representing property "property_editable"."""
    assert node.name == "property_editable"
    assert node.parent == "mock_module.MockClass"
    assert node.kind == "property"
    assert node.signature == "@property\nMockClass.property_editable: int"
    assert node.raw_docstring == (
        "Editable property docstring.\n\n:return: An integer."
    )
    assert node.header_level == 4


def check_property_property_readonly(node: minidoc.Member) -> None:
    """Check node for representing property "property_readonly"."""
    assert node.name == "property_readonly"
    assert node.parent == "mock_module.MockClass"
    assert node.kind == "property"
    assert node.signature == "@property\nMockClass.property_readonly: int"
    assert node.raw_docstring == (
        "Readonly property docstring.\n\n:return: An integer."
    )
    assert node.header_level == 4


def check_class_mock_class(node: minidoc.Member) -> None:
    """Check node for representing class "MockClass"."""
    assert node.name == "MockClass"
    assert node.parent == "mock_module"
    assert node.kind == "class"
    assert node.signature == "MockClass(object)"
    assert node.raw_docstring == "Mock class docstring."
    assert node.header_level == 3
    assert len(node.children) == 7

    # Check children
    check_classvar_class_var(node.children[0])
    check_classvar_undocumented(node.children[1])
    check_property_property_readonly(node.children[2])
    check_property_property_editable(node.children[3])
    check_method_public_method(node.children[4])
    check_method_class_method(node.children[5])
    check_method_static_method(node.children[6])


def check_class_child_class(node: minidoc.Member) -> None:
    """Check node for representing class "ChildClass"."""
    assert node.name == "ChildClass"
    assert node.parent == "mock_module"
    assert node.kind == "class"
    assert node.signature == "ChildClass(MockClass)"
    assert node.raw_docstring == "Child class docstring."
    assert node.header_level == 3
    assert len(node.children) == 2

    assert node.children[0].name == "class_var"
    assert node.children[0].kind == "classvar"
    assert node.children[1].name == "new_method"
    assert node.children[1].kind == "method"


def check_class_grandchild_class(node: minidoc.Member) -> None:
    """Check node for representing class "GrandChildClass"."""
    assert node.name == "GrandchildClass"
    assert node.parent == "mock_module"
    assert node.kind == "class"
    assert node.signature == "GrandchildClass(ChildClass)"
    assert node.raw_docstring == "Grandchild class docstring."
    assert node.header_level == 3
    assert len(node.children) == 0


def check_class_multiple_parents(node: minidoc.Member) -> None:
    """Check node for representing class "MultipleParents"."""
    assert node.name == "MultipleParents"
    assert node.parent == "mock_module"
    assert node.kind == "class"
    assert node.signature == "MultipleParents(MockClass, AnotherParent)"
    assert node.raw_docstring == "Multiple parents class docstring."
    assert node.header_level == 3
    assert len(node.children) == 0


def check_class_mock_dataclass(node: minidoc.Member) -> None:
    """Check node for representing dataclass "MockDataclass"."""
    assert node.name == "MockDataclass"
    assert node.parent == "mock_module"
    assert node.kind == "dataclass"
    assert node.signature == "@dataclass\nMockDataclass(object)"
    assert node.raw_docstring == "Mock dataclass docstring."
    assert node.header_level == 3
    assert len(node.children) == 3

    # Check children
    assert node.children[0].name == "class_var"
    assert node.children[0].parent == "mock_module.MockDataclass"
    assert node.children[0].kind == "classvar"
    assert (
        node.children[0].signature
        == "MockDataclass.class_var: ClassVar[int] = 0"
    )
    assert node.children[0].raw_docstring == ""
    assert node.children[0].header_level == 4

    assert node.children[1].name == "undocumented"
    assert node.children[1].parent == "mock_module.MockDataclass"
    assert node.children[1].kind == "classvar"
    assert (
        node.children[1].signature
        == "MockDataclass.undocumented: ClassVar[bool] = False"
    )
    assert node.children[1].raw_docstring == ""
    assert node.children[1].header_level == 4

    assert node.children[2].name == "public_method"
    assert node.children[2].parent == "mock_module.MockDataclass"
    assert node.children[2].kind == "method"
    assert node.children[2].signature == (
        "MockDataclass.public_method(self, param_c: bool, "
        "optional: str | None = None) -> int"
    )
    assert node.children[2].raw_docstring == (
        "Public method docstring.\n\n"
        ":param param_c: Parameter C.\n"
        ":param optional: An optional parameter.\n"
        ":return: An integer."
    )
    assert node.children[2].header_level == 4


# == MEMBER FUNCTION TESTS =============================================


def test_member_constant_with_docstring(mock_module: ModuleType) -> None:
    """Test the function for a member with a constant value."""
    output = minidoc._member_constant(
        "MOCK_CONSTANT", mock_module.MOCK_CONSTANT, "mock_module"
    )
    check_constant_mock_constant(output)


def test_member_constant_no_docstring(mock_module: ModuleType) -> None:
    """Test the function for a member with a constant value."""
    output = minidoc._member_constant(
        "UNDOCUMENTED", mock_module.UNDOCUMENTED, "mock_module"
    )
    check_constant_undocumented(output)


def test_member_function(mock_module: ModuleType) -> None:
    """Test the function for a member function."""
    output = minidoc._member_function(
        "mock_function", mock_module.mock_function, "mock_module"
    )
    check_function_mock_function(output)


def test_member_function_custom_types(mock_module: ModuleType) -> None:
    """Test the function for a member function with non-builtin types."""
    output = minidoc._member_function(
        "function_with_custom_type",
        mock_module.function_with_custom_type,
        "mock_module",
    )
    check_function_function_with_custom_type(output)


def test_member_method_basic(mock_module: ModuleType) -> None:
    """Test the function for a method."""
    output = minidoc._member_method(
        "public_method",
        mock_module.MockClass.public_method,
        "mock_module.MockClass",
        None,
    )
    check_method_public_method(output)


def test_member_method_decorated(mock_module: ModuleType) -> None:
    """Test the function for a decorated method."""
    output = minidoc._member_method(
        "public_method",
        mock_module.MockClass.public_method,
        "mock_module.MockClass",
        "decorator",
    )
    assert output.name == "public_method"
    assert output.parent == "mock_module.MockClass"
    assert output.kind == "method"
    assert output.signature == (
        "@decorator\nMockClass.public_method(self, param_c: bool, "
        "optional: str | None = None) -> int"
    )
    assert output.raw_docstring == (
        "Public method docstring.\n\n"
        ":param param_c: Parameter C.\n"
        ":param optional: Optional parameter.\n"
        ":return: An integer."
    )
    assert output.header_level == 4


def test_member_method_classmethod(mock_module: ModuleType) -> None:
    """Test the function for a class method."""
    output = minidoc._member_method(
        "class_method",
        mock_module.MockClass.class_method,
        "mock_module.MockClass",
        "classmethod",
    )
    check_method_class_method(output)


def test_member_method_staticmethod(mock_module: ModuleType) -> None:
    """Test the function for a static method."""
    output = minidoc._member_method(
        "static_method",
        mock_module.MockClass.static_method,
        "mock_module.MockClass",
        "staticmethod",
    )
    check_method_static_method(output)


def test_member_classvar(mock_module: ModuleType) -> None:
    """Test the function for a classvar."""
    output = minidoc._member_classvar(
        "class_var", mock_module.MockClass.class_var, "mock_module.MockClass"
    )
    check_classvar_class_var(output)


def test_member_classvar_no_docs(mock_module: ModuleType) -> None:
    """Test the function for a classvar without docstring."""
    output = minidoc._member_classvar(
        "undocumented",
        mock_module.MockClass.undocumented,
        "mock_module.MockClass",
    )
    check_classvar_undocumented(output)


def test_member_property(mock_module: ModuleType) -> None:
    """Test the function for a property."""
    output = minidoc._member_property(
        "property_editable",
        mock_module.MockClass.property_editable,
        "mock_module.MockClass",
    )
    check_property_property_editable(output)


def test_member_class_normal(mock_module: ModuleType) -> None:
    """Test the function for a class."""
    output = minidoc._member_class(
        "MockClass", mock_module.MockClass, "mock_module"
    )
    check_class_mock_class(output)


def test_member_class_inheritance(mock_module: ModuleType) -> None:
    """Test the function for a class with a parent class."""
    output = minidoc._member_class(
        "ChildClass", mock_module.ChildClass, "mock_module"
    )
    check_class_child_class(output)


def test_member_class_inheritance_chain(mock_module: ModuleType) -> None:
    """Test the function for a class further down an inheritance chain."""
    output = minidoc._member_class(
        "GrandchildClass", mock_module.GrandchildClass, "mock_module"
    )
    check_class_grandchild_class(output)


def test_member_class_multiple_inheritance(mock_module: ModuleType) -> None:
    """Test the function for a class with multiple parents."""
    output = minidoc._member_class(
        "MultipleParents", mock_module.MultipleParents, "mock_module"
    )
    check_class_multiple_parents(output)


def test_member_class_dataclass(mock_module: ModuleType) -> None:
    """Test the function for a dataclass."""
    output = minidoc._member_class(
        "MockDataclass", mock_module.MockDataclass, "mock_module"
    )
    check_class_mock_dataclass(output)


def test_member_module(mock_module: ModuleType) -> None:
    """Test the function for a module."""
    test_config = config.MinidocConfig()
    output = minidoc._member_module(
        "mock_module", mock_module, test_config, "mock_module", ""
    )
    assert output.name == "mock_module"
    assert output.parent == ""
    assert output.kind == "module"
    assert output.signature == ""
    assert output.raw_docstring == "Mock module docstring."
    assert output.header_level == 2
    for child in output.children:
        print(child)
    assert len(output.children) == 10

    # check children
    check_constant_mock_constant(output.children[0])
    check_constant_undocumented(output.children[1])
    check_function_mock_function(output.children[2])
    check_class_mock_class(output.children[3])
    check_class_child_class(output.children[4])
    check_class_grandchild_class(output.children[5])
    # missing here: the class "AnotherParent", verified below
    check_class_multiple_parents(output.children[7])
    check_class_mock_dataclass(output.children[8])
    check_function_function_with_custom_type(output.children[9])

    # check AnotherParent class
    node = output.children[6]
    assert node.name == "AnotherParent"
    assert node.parent == "mock_module"
    assert node.kind == "class"
    assert node.signature == "AnotherParent(object)"
    assert node.raw_docstring == "Another parent class docstring."
    assert node.header_level == 3
    assert len(node.children) == 0


def test_member_module_parent(mock_module: ModuleType) -> None:
    """Test the function for a module with a parent."""
    test_config = config.MinidocConfig()
    output = minidoc._member_module(
        "mock_module", mock_module, test_config, "mock_module", "parent"
    )
    assert output.name == "mock_module"
    assert output.parent == "parent"
    assert output.kind == "module"
    assert output.signature == ""
    assert output.raw_docstring == "Mock module docstring."
    assert output.header_level == 2
    assert len(output.children) == 10
    for child in output.children:
        assert child.parent == "parent.mock_module"


def test_member_module_no_constants(mock_module: ModuleType) -> None:
    """Test the function for a module."""
    test_config = config.MinidocConfig(document_constants=False)
    output = minidoc._member_module(
        "mock_module", mock_module, test_config, "mock_module", ""
    )
    assert output.name == "mock_module"
    assert output.parent == ""
    assert output.kind == "module"
    assert output.signature == ""
    assert output.raw_docstring == "Mock module docstring."
    assert output.header_level == 2
    assert len(output.children) == 8

    # check children
    check_function_mock_function(output.children[0])
    check_class_mock_class(output.children[1])
    check_class_child_class(output.children[2])
    check_class_grandchild_class(output.children[3])
    # missing here: the class "AnotherParent", verified below
    check_class_multiple_parents(output.children[5])
    check_class_mock_dataclass(output.children[6])
    check_function_function_with_custom_type(output.children[7])

    # check AnotherParent class
    node = output.children[4]
    assert node.name == "AnotherParent"
    assert node.parent == "mock_module"
    assert node.kind == "class"
    assert node.signature == "AnotherParent(object)"
    assert node.raw_docstring == "Another parent class docstring."
    assert node.header_level == 3
    assert len(node.children) == 0


# == FUNCTIONS FOR BUILDING THE DOCS ===================================


def test_build_toc() -> None:
    """Test the function to create TOC lists."""

    @dataclass
    class MockMember:
        name: str
        kind: str
        parent: str
        children: list[MockMember] = field(default_factory=list)

    # build a small mock hierarchy
    subsubmember_1 = MockMember("sub-sub-member 1", "class", "subsubparent")
    subsubmember_2 = MockMember("sub-sub-member 2", "function", "subsubparent")
    subsubmodule = MockMember(
        "subsubmodule", "module", "submodule", [subsubmember_1, subsubmember_2]
    )
    submember_1 = MockMember("sub-member 1", "class", "subparent")
    submember_2 = MockMember("sub-member 2", "function", "subparent")
    submodule = MockMember(
        "submodule",
        "module",
        "module",
        [submember_1, submember_2, subsubmodule],
    )
    member_1 = MockMember("member 1", "class", "module")
    member_2 = MockMember("member 2", "function", "module")
    module = MockMember("module", "class", "", [member_1, member_2, submodule])

    # test the function
    test_config = config.MinidocConfig()
    toc = minidoc._build_toc(
        module,  # pyrefly: ignore[bad-argument-type]
        test_config,
    )

    # check output
    expected = (
        "> - [`module`](#module)\n"
        ">   - [`module.member 1`](#modulemember-1)\n"
        ">   - [`module.member 2`](#modulemember-2)\n"
        "> - [`module.submodule`](#modulesubmodule)\n"
        ">   - [`subparent.sub-member 1`](#subparentsub-member-1)\n"
        ">   - [`subparent.sub-member 2`](#subparentsub-member-2)\n"
        "> - [`submodule.subsubmodule`](#submodulesubsubmodule)\n"
        ">   - [`subsubparent.sub-sub-member 1`](#subsubparentsub-sub-member-1)\n"
        ">   - [`subsubparent.sub-sub-member 2`](#subsubparentsub-sub-member-2)\n"
    )
    assert toc == expected
