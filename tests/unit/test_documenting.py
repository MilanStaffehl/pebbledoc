"""Unit tests for the documenting module."""

from __future__ import annotations

from dataclasses import dataclass, field
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from pebbledoc import config, documenting, inspect_runtime


@dataclass
class MockMember:
    name: str
    kind: str
    parent: str
    children: list[MockMember] = field(default_factory=list)


@pytest.fixture
def patch_parse_docstring(mocker: MockerFixture) -> Mock:
    """Patch the function to parse docstrings."""
    mock_parse_docstring = mocker.patch(
        "pebbledoc.parsing.parse_docstring",
        side_effect=lambda d, c, vt: f"{d.rstrip('\n')}\n",
    )
    return mock_parse_docstring


@pytest.fixture
def mock_toc_module() -> MockMember:
    """Build a mock member hierarchy to test TOC building."""
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

    return module


# == TESTS FOR _VALID_REFERENCE_TARGETS ================================
def test_valid_reference_targets_single_member() -> None:
    """Test the function for a single member with no children."""
    test_member = inspect_runtime.Member(
        name="test_member",
        parent="parent",
        kind="test_kind",
        signature="test_member = pytest.mock.Mock()",
        raw_docstring="Mock docstring",
        header_level=3,
    )
    output = documenting._valid_reference_targets(test_member)
    expected = {"parent.test_member", "test_member"}
    assert output == expected


def test_valid_reference_targets_member_tree() -> None:
    """Test the function for a member tree with children."""
    child_one = inspect_runtime.Member(
        name="child_one",
        parent="parent.test_member",
        kind="test_kind",
        signature="test_member = pytest.mock.Mock()",
        raw_docstring="This is child one's docstring.\n\n",
        header_level=4,
    )
    child_two = inspect_runtime.Member(
        name="child_two",
        parent="parent.test_member",
        kind="test_kind",
        signature="test_member = pytest.mock.Mock()",
        raw_docstring="This is child two's docstring.\n\n",
        header_level=4,
    )
    test_member = inspect_runtime.Member(
        name="test_member",
        parent="parent",
        kind="test_kind",
        signature="test_member = pytest.mock.Mock()",
        raw_docstring="This is a test docstring.",
        header_level=3,
        children=[child_one, child_two],
    )
    output = documenting._valid_reference_targets(test_member)
    expected = {
        "parent.test_member",
        "test_member",
        "parent.test_member.child_one",
        "test_member.child_one",
        "child_one",
        "parent.test_member.child_two",
        "test_member.child_two",
        "child_two",
    }
    assert output == expected


# == TESTS FOR _DOCUMENT_MEMBER ========================================


def test_document_member_all_fields(patch_parse_docstring: Mock) -> None:
    """Test the function for a member with all fields."""

    test_config = config.PebbledocConfig(package_name="parent")
    test_docstring = "This is a test docstring."
    test_member = inspect_runtime.Member(
        name="test_member",
        parent="parent",
        kind="test_kind",
        signature="test_member = pytest.mock.Mock()",
        raw_docstring=test_docstring,
        header_level=3,
    )

    output = documenting._document_member(test_member, test_config)
    expected = (
        '<a name="test_member"></a>\n'
        "### `parent.test_member`\n\n"
        "<sup>[Back to top](#parent-documentation)</sup>\n\n"
        "```Python\n"
        "test_member = pytest.mock.Mock()\n"
        "```\n\n"
        "This is a test docstring.\n\n"
    )
    assert output == expected
    patch_parse_docstring.assert_called_once_with(
        test_docstring, test_config, None
    )


def test_document_member_parent_hierarchy(patch_parse_docstring: Mock) -> None:
    """Test the function adds anchors for all parents, except full name."""

    test_config = config.PebbledocConfig(package_name="parent")
    test_docstring = "This is a test docstring."
    test_member = inspect_runtime.Member(
        name="test_member",
        parent="parent.subparent.subcontainer",
        kind="test_kind",
        signature="test_member = pytest.mock.Mock()",
        raw_docstring=test_docstring,
        header_level=3,
    )

    output = documenting._document_member(test_member, test_config)
    expected = (
        '<a name="subparentsubcontainertest_member"></a>\n'
        '<a name="subcontainertest_member"></a>\n'
        '<a name="test_member"></a>\n'
        "### `parent.subparent.subcontainer.test_member`\n\n"
        "<sup>[Back to top](#parent-documentation)</sup>\n\n"
        "```Python\n"
        "test_member = pytest.mock.Mock()\n"
        "```\n\n"
        "This is a test docstring.\n\n"
    )
    assert output == expected
    patch_parse_docstring.assert_called_once_with(
        test_docstring, test_config, None
    )


def test_document_member_no_docstring(patch_parse_docstring: Mock) -> None:
    """Test the function for a member with no docstring."""

    test_config = config.PebbledocConfig(package_name="parent")
    test_member = inspect_runtime.Member(
        name="test_member",
        parent="parent",
        kind="test_kind",
        signature="test_member = pytest.mock.Mock()",
        raw_docstring="",
        header_level=3,
    )

    output = documenting._document_member(test_member, test_config)
    expected = (
        '<a name="test_member"></a>\n'
        "### `parent.test_member`\n\n"
        "<sup>[Back to top](#parent-documentation)</sup>\n\n"
        "```Python\ntest_member = "
        "pytest.mock.Mock()\n```\n\n"
    )
    assert output == expected
    patch_parse_docstring.assert_not_called()


def test_document_member_no_signature(patch_parse_docstring: Mock) -> None:
    """Test the function for a member with no signature."""

    test_config = config.PebbledocConfig(package_name="parent")
    test_docstring = "This is a test docstring."
    test_member = inspect_runtime.Member(
        name="test_member",
        parent="parent",
        kind="test_kind",
        signature="",
        raw_docstring=test_docstring,
        header_level=3,
    )

    output = documenting._document_member(test_member, test_config)
    expected = (
        '<a name="test_member"></a>\n'
        "### `parent.test_member`\n\n"
        "<sup>[Back to top](#parent-documentation)</sup>\n\n"
        "This is a test docstring.\n\n"
    )
    assert output == expected
    patch_parse_docstring.assert_called_once_with(
        test_docstring, test_config, None
    )


def test_document_member_header_level(patch_parse_docstring: Mock) -> None:
    """Test the function for a member with various header levels."""

    test_config = config.PebbledocConfig(package_name="parent")
    test_docstring = "This is a test docstring."
    for lvl in range(1, 4):
        test_member = inspect_runtime.Member(
            name="test_member",
            parent="parent",
            kind="test_kind",
            signature="test_member = pytest.mock.Mock()",
            raw_docstring=test_docstring,
            header_level=lvl,
        )

        output = documenting._document_member(test_member, test_config)
        header_prefix = "#" * lvl
        expected = (
            '<a name="test_member"></a>\n'
            f"{header_prefix} `parent.test_member`\n\n"
            "<sup>[Back to top](#parent-documentation)</sup>\n\n"
            "```Python\n"
            "test_member = pytest.mock.Mock()\n"
            "```\n\n"
            "This is a test docstring.\n\n"
        )
        assert output == expected
        patch_parse_docstring.assert_called_once_with(
            test_docstring, test_config, None
        )
        patch_parse_docstring.reset_mock()


def test_document_member_children(patch_parse_docstring: Mock) -> None:
    """Test the function for a member with children."""

    test_config = config.PebbledocConfig(package_name="parent")
    child_one = inspect_runtime.Member(
        name="child_one",
        parent="parent.test_member",
        kind="test_kind",
        signature="test_member = pytest.mock.Mock()",
        raw_docstring="This is child one's docstring.\n\n",
        header_level=4,
    )
    child_two = inspect_runtime.Member(
        name="child_two",
        parent="parent.test_member",
        kind="test_kind",
        signature="test_member = pytest.mock.Mock()",
        raw_docstring="This is child two's docstring.\n\n",
        header_level=4,
    )
    test_member = inspect_runtime.Member(
        name="test_member",
        parent="parent",
        kind="test_kind",
        signature="test_member = pytest.mock.Mock()",
        raw_docstring="This is a test docstring.",
        header_level=3,
        children=[child_one, child_two],
    )

    output = documenting._document_member(test_member, test_config)
    expected = (
        '<a name="test_member"></a>\n'
        "### `parent.test_member`\n\n"
        "<sup>[Back to top](#parent-documentation)</sup>\n\n"
        "```Python\n"
        "test_member = pytest.mock.Mock()\n"
        "```\n\n"
        "This is a test docstring.\n\n"
        '<a name="test_memberchild_one"></a>\n'
        '<a name="child_one"></a>\n'
        "#### `parent.test_member.child_one`\n\n"
        "<sup>[Back to top](#parent-documentation)</sup>\n\n"
        "```Python\n"
        "test_member = pytest.mock.Mock()\n"
        "```\n\n"
        "This is child one's docstring.\n\n"
        '<a name="test_memberchild_two"></a>\n'
        '<a name="child_two"></a>\n'
        "#### `parent.test_member.child_two`\n\n"
        "<sup>[Back to top](#parent-documentation)</sup>\n\n"
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


def test_document_member_valid_targets(patch_parse_docstring: Mock) -> None:
    """Test the function when a set of valid targets is specified."""

    test_config = config.PebbledocConfig(package_name="parent")
    test_docstring = "This is a test docstring."
    test_member = inspect_runtime.Member(
        name="test_member",
        parent="parent",
        kind="test_kind",
        signature="test_member = pytest.mock.Mock()",
        raw_docstring=test_docstring,
        header_level=3,
    )

    valid_targets = {"parent.test_member", "test_member"}
    output = documenting._document_member(
        test_member, test_config, valid_targets
    )
    expected = (
        '<a name="test_member"></a>\n'
        "### `parent.test_member`\n\n"
        "<sup>[Back to top](#parent-documentation)</sup>\n\n"
        "```Python\n"
        "test_member = pytest.mock.Mock()\n"
        "```\n\n"
        "This is a test docstring.\n\n"
    )
    assert output == expected
    patch_parse_docstring.assert_called_once_with(
        test_docstring, test_config, valid_targets
    )


def test_document_member_no_back_to_top(patch_parse_docstring: Mock) -> None:
    """Test the function for a member with "Back to top" links disabled."""

    test_config = config.PebbledocConfig(include_back_to_top=False)
    test_docstring = "This is a test docstring."
    test_member = inspect_runtime.Member(
        name="test_member",
        parent="parent",
        kind="test_kind",
        signature="test_member = pytest.mock.Mock()",
        raw_docstring=test_docstring,
        header_level=3,
    )

    output = documenting._document_member(test_member, test_config)
    expected = (
        '<a name="test_member"></a>\n'
        "### `parent.test_member`\n\n"
        "```Python\n"
        "test_member = pytest.mock.Mock()\n"
        "```\n\n"
        "This is a test docstring.\n\n"
    )
    assert output == expected
    patch_parse_docstring.assert_called_once_with(
        test_docstring, test_config, None
    )


def test_document_member_custom_document_title(
    patch_parse_docstring: Mock,
) -> None:
    """Test the function when the document has a custom title."""

    test_config = config.PebbledocConfig(
        document_title="Custom document title"
    )
    test_docstring = "This is a test docstring."
    test_member = inspect_runtime.Member(
        name="test_member",
        parent="parent",
        kind="test_kind",
        signature="test_member = pytest.mock.Mock()",
        raw_docstring=test_docstring,
        header_level=3,
    )

    output = documenting._document_member(test_member, test_config)
    expected = (
        '<a name="test_member"></a>\n'
        "### `parent.test_member`\n\n"
        "<sup>[Back to top](#custom-document-title)</sup>\n\n"
        "```Python\n"
        "test_member = pytest.mock.Mock()\n"
        "```\n\n"
        "This is a test docstring.\n\n"
    )
    assert output == expected
    patch_parse_docstring.assert_called_once_with(
        test_docstring, test_config, None
    )


def test_document_member_no_main_module_header(
    patch_parse_docstring: Mock,
) -> None:
    """Test the function when main module headers are disabled."""
    test_docstring = "This is a test docstring."
    test_member = inspect_runtime.Member(
        name="test_member",
        parent="",
        kind="test_kind",
        signature="",
        raw_docstring=test_docstring,
        header_level=2,
    )

    # test behavior with the option disabled
    test_config = config.PebbledocConfig(package_name="test_member")
    output = documenting._document_member(test_member, test_config)
    expected = (
        "## `test_member`\n\n"
        "<sup>[Back to top](#test_member-documentation)</sup>\n\n"
        "This is a test docstring.\n\n"
    )
    assert output == expected
    patch_parse_docstring.assert_called_once_with(
        test_docstring, test_config, None
    )
    patch_parse_docstring.reset_mock()

    # ...and once with the option enabled
    test_config = config.PebbledocConfig(
        package_name="test_member", main_module_header=False
    )
    output = documenting._document_member(test_member, test_config)
    expected = "This is a test docstring.\n\n"
    assert output == expected
    patch_parse_docstring.assert_called_once_with(
        test_docstring, test_config, None
    )


# == FUNCTIONS FOR BUILDING THE DOCS ===================================


def test_build_toc(mock_toc_module: MockMember) -> None:
    """Test the function to create TOC lists."""
    # test the function
    test_config = config.PebbledocConfig(package_name="module")
    toc = documenting._build_toc(
        mock_toc_module,  # pyrefly: ignore[bad-argument-type]
        test_config,
    )

    # check output
    expected = (
        "- [`module`](#module)\n"
        "  - [`module.member 1`](#modulemember-1)\n"
        "  - [`module.member 2`](#modulemember-2)\n"
        "- [`module.submodule`](#modulesubmodule)\n"
        "  - [`subparent.sub-member 1`](#subparentsub-member-1)\n"
        "  - [`subparent.sub-member 2`](#subparentsub-member-2)\n"
        "- [`submodule.subsubmodule`](#submodulesubsubmodule)\n"
        "  - [`subsubparent.sub-sub-member 1`](#subsubparentsub-sub-member-1)\n"
        "  - [`subsubparent.sub-sub-member 2`](#subsubparentsub-sub-member-2)\n"
    )
    assert toc == expected


def test_build_toc_no_main_module_header(mock_toc_module: MockMember) -> None:
    """Test the function to create TOC list without the main module header."""
    # test the function
    test_config = config.PebbledocConfig(
        package_name="module", main_module_header=False
    )
    toc = documenting._build_toc(
        mock_toc_module,  # pyrefly: ignore[bad-argument-type]
        test_config,
    )

    # check output
    expected = (
        "- [`module.member 1`](#modulemember-1)\n"
        "- [`module.member 2`](#modulemember-2)\n"
        "- [`module.submodule`](#modulesubmodule)\n"
        "  - [`subparent.sub-member 1`](#subparentsub-member-1)\n"
        "  - [`subparent.sub-member 2`](#subparentsub-member-2)\n"
        "- [`submodule.subsubmodule`](#submodulesubsubmodule)\n"
        "  - [`subsubparent.sub-sub-member 1`](#subsubparentsub-sub-member-1)\n"
        "  - [`subsubparent.sub-sub-member 2`](#subsubparentsub-sub-member-2)\n"
    )
    assert toc == expected


def test_build_toc_no_full_name(mock_toc_module: MockMember) -> None:
    """Test the function to create TOC lists with shortened names."""
    # test the function
    test_config = config.PebbledocConfig(
        package_name="module", full_toc_name=False
    )
    toc = documenting._build_toc(
        mock_toc_module,  # pyrefly: ignore[bad-argument-type]
        test_config,
    )

    # check output
    expected = (
        "- [`module`](#module)\n"
        "  - [`member 1`](#modulemember-1)\n"
        "  - [`member 2`](#modulemember-2)\n"
        "- [`module.submodule`](#modulesubmodule)\n"
        "  - [`sub-member 1`](#subparentsub-member-1)\n"
        "  - [`sub-member 2`](#subparentsub-member-2)\n"
        "- [`submodule.subsubmodule`](#submodulesubsubmodule)\n"
        "  - [`sub-sub-member 1`](#subsubparentsub-sub-member-1)\n"
        "  - [`sub-sub-member 2`](#subsubparentsub-sub-member-2)\n"
    )
    assert toc == expected


def test_build_toc_no_full_name_no_main_module_header(
    mock_toc_module: MockMember,
) -> None:
    """Test the function with shortened names and no main module header."""
    # test the function
    test_config = config.PebbledocConfig(
        package_name="module",
        full_toc_name=False,
        main_module_header=False,
    )
    toc = documenting._build_toc(
        mock_toc_module,  # pyrefly: ignore[bad-argument-type]
        test_config,
    )

    # check output
    expected = (
        "- [`member 1`](#modulemember-1)\n"
        "- [`member 2`](#modulemember-2)\n"
        "- [`submodule`](#modulesubmodule)\n"
        "  - [`sub-member 1`](#subparentsub-member-1)\n"
        "  - [`sub-member 2`](#subparentsub-member-2)\n"
        "- [`subsubmodule`](#submodulesubsubmodule)\n"
        "  - [`sub-sub-member 1`](#subsubparentsub-sub-member-1)\n"
        "  - [`sub-sub-member 2`](#subsubparentsub-sub-member-2)\n"
    )
    assert toc == expected
