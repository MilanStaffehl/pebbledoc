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
