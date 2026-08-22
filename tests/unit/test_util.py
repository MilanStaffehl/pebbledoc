"""Tests for the util module."""

from pebbledoc import util


def test_name_to_ref_plain() -> None:
    """Test the function for a plain text name."""
    output = util.name_to_ref("textname")
    assert output == "textname"


def test_name_to_ref_underscore() -> None:
    """Test underscores are preserved."""
    output = util.name_to_ref("text_name")
    assert output == "text_name"


def test_name_to_ref_dashes() -> None:
    """Test dashes are preserved."""
    output = util.name_to_ref("text-name")
    assert output == "text-name"


def test_name_to_ref_dots() -> None:
    """Test dots are removed."""
    output = util.name_to_ref("text.name")
    assert output == "textname"


def test_name_to_ref_space() -> None:
    """Test spaces are removed."""
    output = util.name_to_ref("text name")
    assert output == "text-name"


def test_name_to_ref_numbers() -> None:
    """Test numbers are preserved."""
    output = util.name_to_ref("text01234")
    assert output == "text01234"


def test_name_to_ref_leading_underscore() -> None:
    """Test leading underscores are preserved."""
    output = util.name_to_ref("_text_name")
    assert output == "_text_name"


def test_name_to_ref_backticks() -> None:
    """Test backticks are removed."""
    output = util.name_to_ref("`text_name`")
    assert output == "text_name"


def test_full_qualified_name() -> None:
    """Test constructing a full qualified name."""
    output = util.full_qualified_name("member", "parent")
    assert output == "parent.member"


def test_full_qualified_name_longer_parent() -> None:
    """Test constructing a full qualified name with a longer parent."""
    output = util.full_qualified_name("member", "module.parent")
    assert output == "module.parent.member"


def test_full_qualified_name_no_parent() -> None:
    """Test constructing a full qualified name without a parent."""
    output = util.full_qualified_name("member", "")
    assert output == "member"


def test_all_qualified_names() -> None:
    """Test finding all qualified names."""
    output = util.all_qualified_names("member", "parent")
    assert output == {"parent.member", "member"}


def test_all_qualified_names_longer_parent() -> None:
    """Test finding all qualified names with a longer parent."""
    output = util.all_qualified_names("member", "package.module.parent")
    expected = {
        "package.module.parent.member",
        "module.parent.member",
        "parent.member",
        "member",
    }
    assert output == expected


def test_all_qualified_names_no_parent() -> None:
    """all qualified names without a parent."""
    output = util.all_qualified_names("member", "")
    assert output == {"member"}
