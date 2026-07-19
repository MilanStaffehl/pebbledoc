"""Tests for the parsing module."""

import inspect
from pathlib import Path

import pytest

from minidoc_md import config, parsing, types

_ADMONITION_NAMES = [
    "attention",
    "caution",
    "danger",
    "error",
    "hint",
    "important",
    "note",
    "tip",
    "warning",
]


@pytest.fixture
def mock_docstring() -> str:
    """Return a test docstring, normalized by ``inspect``."""
    with open(Path(__file__).parent / "resources" / "source.rst") as f:
        mock_docs = f.read()
    return inspect.cleandoc(mock_docs)


@pytest.fixture
def expected_output_base() -> str:
    """Return the expected output for the default config."""
    with open(Path(__file__).parent / "resources" / "expected_base.md") as f:
        expected_base = f.read()
    return expected_base


# == INDIVIDUAL FEATURES ===============================================
def test_parse_docstring_paragraph() -> None:
    """Test parsing a simple paragraph."""
    default_config = config.MinidocConfig()
    rst_str = "This is a simple paragraph."
    output = parsing.parse_docstring(rst_str, default_config)
    expected = "This is a simple paragraph.\n\n"
    assert output == expected


def test_parse_docstring_paragraph_with_line_break() -> None:
    """Test parsing a paragraph with a stylistic line break (line wrap)."""
    default_config = config.MinidocConfig()
    rst_str = "This is a simple paragraph.\nIt is wrapped at the line end."
    output = parsing.parse_docstring(rst_str, default_config)
    expected = "This is a simple paragraph.\nIt is wrapped at the line end.\n\n"
    assert output == expected


def test_parse_docstring_emphasize() -> None:
    """Test parsing a paragraph with emphasized text."""
    default_config = config.MinidocConfig()
    rst_str = "This paragraph has *emphasized* text."
    output = parsing.parse_docstring(rst_str, default_config)
    expected = "This paragraph has *emphasized* text.\n\n"
    assert output == expected


def test_parse_docstring_strong() -> None:
    """Test parsing a paragraph with strongly emphasized text."""
    default_config = config.MinidocConfig()
    rst_str = "This paragraph has **strong emphasize**."
    output = parsing.parse_docstring(rst_str, default_config)
    expected = "This paragraph has **strong emphasize**.\n\n"
    assert output == expected


def test_parse_docstring_interpreted_text() -> None:
    """Test parsing text with interpreted text (default role)."""
    default_config = config.MinidocConfig()
    rst_str = "This text contains `interpreted` text."
    output = parsing.parse_docstring(rst_str, default_config)
    expected = "This text contains `interpreted` text.\n\n"
    assert output == expected


def test_parse_docstring_simple_bullet_list() -> None:
    """Test parsing a simple bullet list."""
    default_config = config.MinidocConfig()
    rst_str = "- List item one.\n- List item two.\n- List item three.\n"
    output = parsing.parse_docstring(rst_str, default_config)
    assert output == rst_str + "\n"  # result is identical, plus line break


def test_parse_docstring_nested_bullet_list() -> None:
    """Test parsing a nested bullet list."""
    default_config = config.MinidocConfig()
    rst_str = (
        "- List item one.\n\n"
        "  - Nested bullet list.\n\n"
        "- List item two.\n\n"
        "  - Nested item one.\n"
        "  - Nested item two.\n\n"
        "- List item three.\n"
    )
    output = parsing.parse_docstring(rst_str, default_config)
    # remove required double line breaks from rst
    expected = (
        "- List item one.\n"
        "  - Nested bullet list.\n"
        "- List item two.\n"
        "  - Nested item one.\n"
        "  - Nested item two.\n"
        "- List item three.\n\n"
    )
    assert output == expected


def test_parse_docstring_simple_enumerated_list() -> None:
    """Test parsing a simple enumerated list."""
    default_config = config.MinidocConfig()
    rst_str = "1. List item one.\n2. List item two.\n3. List item three.\n"
    output = parsing.parse_docstring(rst_str, default_config)
    assert output == rst_str + "\n"  # result is identical, plus line break


def test_parse_docstring_nested_enumerated_list() -> None:
    """Test parsing a nested bullet list."""
    default_config = config.MinidocConfig()
    rst_str = (
        "1. List item one.\n\n"
        "   1. Nested enum list.\n\n"
        "2. List item two.\n\n"
        "   1. Nested item one.\n"
        "   2. Nested item two.\n\n"
        "3. List item three.\n"
    )
    output = parsing.parse_docstring(rst_str, default_config)
    # remove required double line breaks from rst
    expected = (
        "1. List item one.\n"
        "   1. Nested enum list.\n"
        "2. List item two.\n"
        "   1. Nested item one.\n"
        "   2. Nested item two.\n"
        "3. List item three.\n\n"
    )
    assert output == expected


def test_parse_docstring_enumerated_list_later_start() -> None:
    """Test parsing an enumerated list that does not start at 1."""
    default_config = config.MinidocConfig()
    rst_str = "4. List item one.\n5. List item two.\n6. List item three.\n"
    output = parsing.parse_docstring(rst_str, default_config)
    assert output == rst_str + "\n"  # result is identical, plus line break


def test_parse_docstring_mixed_nested_lists() -> None:
    """Test parsing a mixed nested lists."""
    default_config = config.MinidocConfig()

    # Bullet list in enumerated list
    rst_str = (
        "1. List item one.\n\n"
        "   - Nested bullet list.\n\n"
        "2. List item two.\n\n"
        "   - Nested item one.\n"
        "   - Nested item two.\n\n"
        "3. List item three.\n"
    )
    output = parsing.parse_docstring(rst_str, default_config)
    # remove required double line breaks from rst
    expected = (
        "1. List item one.\n"
        "   - Nested bullet list.\n"
        "2. List item two.\n"
        "   - Nested item one.\n"
        "   - Nested item two.\n"
        "3. List item three.\n\n"
    )
    assert output == expected

    # Enumerated list inside bullet list
    rst_str = (
        "- List item one.\n\n"
        "  1. Nested bullet list.\n\n"
        "- List item two.\n\n"
        "  1. Nested item one.\n"
        "  2. Nested item two.\n\n"
        "- List item three.\n"
    )
    output = parsing.parse_docstring(rst_str, default_config)
    # remove required double line breaks from rst
    expected = (
        "- List item one.\n"
        "  1. Nested bullet list.\n"
        "- List item two.\n"
        "  1. Nested item one.\n"
        "  2. Nested item two.\n"
        "- List item three.\n\n"
    )
    assert output == expected


def test_parse_docstring_literal_block() -> None:
    """Test parsing a literal block."""
    default_config = config.MinidocConfig()
    rst_str = (
        "This is a preceding paragraph. ::\n\n"
        "    This is a literal block.\n"
        "    It should render as such.\n\n"
        "This is a closing paragraph."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    expected = (
        "This is a preceding paragraph.\n\n"
        "```\n"
        "This is a literal block.\n"
        "It should render as such.\n"
        "```\n\n"
        "This is a closing paragraph.\n\n"
    )
    assert output == expected


def test_parse_docstring_block_quote() -> None:
    """Test parsing a block quote."""
    default_config = config.MinidocConfig()
    rst_str = (
        "This is a preceding paragraph.\n\n"
        "    This is a block quote.\n"
        "    It should render as such.\n\n"
        "    This is a second paragraph in\n"
        "    the block quote.\n\n"
        "This is a closing paragraph."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    expected = (
        "This is a preceding paragraph.\n\n"
        "> This is a block quote.\n"
        "> It should render as such.\n"
        ">\n"
        "> This is a second paragraph in\n"
        "> the block quote.\n\n"
        "This is a closing paragraph.\n\n"
    )
    assert output == expected


def test_parse_docstring_block_quote_with_attribution() -> None:
    """Test parsing a block quote with an atribution."""
    default_config = config.MinidocConfig()
    rst_str = (
        "This is a preceding paragraph.\n\n"
        "    This is a block quote.\n"
        "    It should render as such.\n\n"
        "    -- Albert Einstein\n\n"
        "This is a closing paragraph."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    expected = (
        "This is a preceding paragraph.\n\n"
        "> This is a block quote.\n"
        "> It should render as such.\n"
        ">\n"
        "> -- Albert Einstein\n\n"
        "This is a closing paragraph.\n\n"
    )
    assert output == expected


def test_parse_docstring_doctest_block() -> None:
    """Test parsing a doctest block."""
    default_config = config.MinidocConfig()
    rst_str = (
        "Here is an example:\n\n"
        ">>> import numpy as np\n"
        ">>> x = np.array([1, 2, 3])\n"
        ">>> x.sum()\n"
        "6.0\n\n"
        "Here is a follow-up paragraph."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    expected = (
        "Here is an example:\n\n"
        "```doctest\n"
        ">>> import numpy as np\n"
        ">>> x = np.array([1, 2, 3])\n"
        ">>> x.sum()\n"
        "6.0\n"
        "```\n\n"
        "Here is a follow-up paragraph.\n\n"
    )
    assert output == expected


def test_parse_docstring_comment() -> None:
    """Test parsing a comment block."""
    default_config = config.MinidocConfig()
    rst_str = (
        "This is a preceding paragraph.\n\n"
        ".. This is a comment block.\n\n"
        "This is a closing paragraph."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    expected = (
        "This is a preceding paragraph.\n\n"
        "<!-- This is a comment block. -->\n\n"
        "This is a closing paragraph.\n\n"
    )
    assert output == expected


def test_parse_docstring_standalone_url() -> None:
    """Test parsing a standalone URLs."""
    default_config = config.MinidocConfig()
    rst_str = "This is a paragraph including a link to https://github.com"
    output = parsing.parse_docstring(rst_str, default_config)
    # GitHub can auto-render valid links, nothing needs to be done.
    expected = "This is a paragraph including a link to https://github.com\n\n"
    assert output == expected


def test_parse_docstring_external_hyperlink() -> None:
    """Test parsing an external hyperlinks."""
    default_config = config.MinidocConfig()
    rst_str = "This text contains a link_ to GitHub.\n\n.. _link: https://github.com"
    output = parsing.parse_docstring(rst_str, default_config)
    expected = "This text contains a [link](https://github.com) to GitHub.\n\n"
    assert output == expected

    # link names with whitespace
    default_config = config.MinidocConfig()
    rst_str = (
        "This text contains a `link to GitHub`_.\n\n"
        ".. _link to GitHub: https://github.com"
    )
    output = parsing.parse_docstring(rst_str, default_config)
    expected = "This text contains a [link to GitHub](https://github.com).\n\n"
    assert output == expected


def test_parse_docstring_internal_reference_target() -> None:
    """Test parsing an internal reference to a dedicated target."""
    default_config = config.MinidocConfig()
    rst_str = (
        "This text references an `internal reference`_.\n\n"
        ".. _internal reference:\n\n"
        "This is the target block."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    expected = (
        "This text references an [internal reference](#internal-reference).\n\n"
        '<a name="internal-reference"></a>\n'
        "This is the target block.\n\n"
    )
    assert output == expected


def test_parse_docstring_internal_reference_multiple_targets() -> None:
    """Test parsing internal references targeting the same place."""
    default_config = config.MinidocConfig()
    rst_str = (
        "This text references an `internal reference`_ and a "
        "`second reference`_.\n\n"
        ".. _internal reference:\n\n"
        ".. _second reference:\n\n"
        "This is the target block."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    expected = (
        "This text references an [internal reference](#internal-reference) "
        "and a [second reference](#second-reference).\n\n"
        '<a name="internal-reference"></a>\n'
        '<a name="second-reference"></a>\n'
        "This is the target block.\n\n"
    )
    assert output == expected


def test_parse_docstring_anonymous_reference() -> None:
    """Test parsing an anonymous reference."""
    default_config = config.MinidocConfig()
    rst_str = (
        "This text contains an `anonymous reference`__.\n\n.. __: https://github.com"
    )
    output = parsing.parse_docstring(rst_str, default_config)
    expected = "This text contains an [anonymous reference](https://github.com).\n\n"
    assert output == expected


# TODO: Test for roles subscript and superscript


# == ADMONITIONS =======================================================
def assert_admonition(header: str, actual: str) -> None:
    """Assert the admonition looks as expected."""
    expected = (
        "This is a preceding paragraph.\n\n"
        f"> {header}\n"
        ">\n"
        "> This is the first line of the body.\n"
        "> This is the second line of the body.\n"
        ">\n"
        "> This is a second paragraph.\n\n"
        "This is a closing paragraph.\n\n"
    )
    assert actual == expected


@pytest.mark.parametrize("admonition_name", _ADMONITION_NAMES)
def test_parse_docstring_admonitions_classic(
    admonition_name: str,
) -> None:
    """Test parsing an attention admonition in 'classic' mode."""
    cfg = config.MinidocConfig("classic")
    rst_str = (
        "This is a preceding paragraph.\n\n"
        f".. {admonition_name}::\n\n"
        "    This is the first line of the body.\n"
        "    This is the second line of the body.\n\n"
        "    This is a second paragraph.\n\n"
        "This is a closing paragraph."
    )
    output = parsing.parse_docstring(rst_str, cfg)
    header = f"**{admonition_name.capitalize()}:**"
    assert_admonition(header=header, actual=output)


@pytest.mark.parametrize("admonition_name", _ADMONITION_NAMES)
def test_parse_docstring_admonitions_github(
    admonition_name: str,
) -> None:
    """Test parsing an attention admonition in 'github' mode."""
    cfg = config.MinidocConfig("github")
    rst_str = (
        "This is a preceding paragraph.\n\n"
        f".. {admonition_name}::\n\n"
        "    This is the first line of the body.\n"
        "    This is the second line of the body.\n\n"
        "    This is a second paragraph.\n\n"
        "This is a closing paragraph."
    )
    output = parsing.parse_docstring(rst_str, cfg)
    header = f"[!{admonition_name.upper()}]"
    assert_admonition(header=header, actual=output)


@pytest.mark.parametrize("admonition_name", _ADMONITION_NAMES)
def test_parse_docstring_admonitions_mix(
    admonition_name: str,
) -> None:
    """Test parsing an attention admonition in 'mix' mode."""
    cfg = config.MinidocConfig("mix")
    rst_str = (
        "This is a preceding paragraph.\n\n"
        f".. {admonition_name}::\n\n"
        "    This is the first line of the body.\n"
        "    This is the second line of the body.\n\n"
        "    This is a second paragraph.\n\n"
        "This is a closing paragraph."
    )
    output = parsing.parse_docstring(rst_str, cfg)
    if admonition_name in parsing._admonitions_map.keys():
        header = f"**{admonition_name.capitalize()}:**"
    else:
        header = f"[!{admonition_name.upper()}]"
    assert_admonition(header=header, actual=output)


@pytest.mark.parametrize("admonition_name", _ADMONITION_NAMES)
def test_parse_docstring_admonitions_map(
    admonition_name: str,
) -> None:
    """Test parsing an attention admonition in 'map' mode."""
    cfg = config.MinidocConfig("map")
    rst_str = (
        "This is a preceding paragraph.\n\n"
        f".. {admonition_name}::\n\n"
        "    This is the first line of the body.\n"
        "    This is the second line of the body.\n\n"
        "    This is a second paragraph.\n\n"
        "This is a closing paragraph."
    )
    output = parsing.parse_docstring(rst_str, cfg)
    if admonition_name in parsing._admonitions_map.keys():
        admonition_name = parsing._admonitions_map[admonition_name]
    header = f"[!{admonition_name.upper()}]"
    assert_admonition(header=header, actual=output)


_TEST_DATA = (
    ("classic", "**Custom title:**"),
    ("github", "[!CUSTOM TITLE]"),
    ("mix", "**Custom title:**"),
    ("map", "[!NOTE]"),
)


@pytest.mark.parametrize("strategy,header", _TEST_DATA)
def test_parse_docstring_admonition_plain(
    strategy: types.AdmonitionStrategy, header: str
) -> None:
    """Test parsing a general admonition."""
    cfg = config.MinidocConfig(strategy)
    rst_str = (
        "This is a preceding paragraph.\n\n"
        ".. admonition:: Custom title\n\n"
        "    This is the first line of the body.\n"
        "    This is the second line of the body.\n\n"
        "    This is a second paragraph.\n\n"
        "This is a closing paragraph."
    )
    output = parsing.parse_docstring(rst_str, cfg)
    assert_admonition(header=header, actual=output)


# TODO: test that options are stripped from admonition (such as :collapsible:)


# == FIELD LISTS =======================================================
def test_parse_docstring_param_field_list() -> None:
    """Test parsing a parameter field list."""
    cfg = config.MinidocConfig()
    rst_str = (
        "This is the last paragraph of the docstring.\n\n"
        ":param a: This is a description of parameter ``a``.\n"
        ":param b: This is a description of parameter ``b``\n"
        "    which is a bit longer and more *extravagant*!\n"
        ":raises KeyError: When a key is not found in a ``dict``.\n"
        ":raise ValueError: When the math ain't mathin.\n"
        ":returns: A series of return values."
    )
    output = parsing.parse_docstring(rst_str, cfg)
    expected = (
        "This is the last paragraph of the docstring.\n\n"
        "**Parameters:**\n\n"
        "- `a`: This is a description of parameter `a`.\n"
        "- `b`: This is a description of parameter `b` which is a bit "
        "longer and more *extravagant*!\n\n"
        "**Raises:**\n\n"
        "- `KeyError`: When a key is not found in a `dict`.\n"
        "- `ValueError`: When the math ain't mathin.\n\n"
        "**Returns:**\n\nA series of return values.\n\n"
    )
    assert output == expected


def test_parse_docstring_param_field_list_inline_markup() -> None:
    """Test parsing a parameter field list with complicated inline markup."""
    cfg = config.MinidocConfig()
    rst_str = (
        "This is the last paragraph of the docstring.\n\n"
        ":param a: This is a description of parameter ``a``.\n"
        ":param b: This is a description of parameter ``b``\n"
        "    which is a bit longer and more *extravagant*! It also\n"
        "    contains a list:\n\n"
        "    - Bullet list item one.\n"
        "    - Bullet list item two.\n\n"
        ":returns: A series of return values."
    )
    output = parsing.parse_docstring(rst_str, cfg)
    expected = (
        "This is the last paragraph of the docstring.\n\n"
        "**Parameters:**\n\n"
        "- `a`: This is a description of parameter `a`.\n"
        "- `b`: This is a description of parameter `b` which is a bit "
        "longer and more *extravagant*! It also contains a list:\n"
        "  - Bullet list item one.\n"
        "  - Bullet list item two.\n\n"
        "**Returns:**\n\nA series of return values.\n\n"
    )
    assert output == expected


def test_parse_docstring_param_field_list_return() -> None:
    """Test that the alternative keyword ``return`` is also accepted."""
    cfg = config.MinidocConfig()
    rst_str = (
        "This is the last paragraph of the docstring.\n\n"
        ":param a: This is a description of parameter ``a``.\n"
        ":return: A series of return values."
    )
    output = parsing.parse_docstring(rst_str, cfg)
    expected = (
        "This is the last paragraph of the docstring.\n\n"
        "**Parameters:**\n\n"
        "- `a`: This is a description of parameter `a`.\n\n"
        "**Returns:**\n\nA series of return values.\n\n"
    )
    assert output == expected


def test_parse_docstring_regular_field_list() -> None:
    """Test parsing a regular field list."""
    cfg = config.MinidocConfig()
    rst_str = (
        "This is a preceding paragraph.\n\n"
        ":field Mark: This is the body text for Mark.\n"
        ":field Peter:\n"
        ":field: This guy has no name, it seems. Still, it should work.\n"
        ":author: Author McAuthorface\n"
        ":year: 2026\n"
        ":publisher: Self-published\n\n"
        "This is a follow-up paragraph."
    )
    output = parsing.parse_docstring(rst_str, cfg)
    expected = (
        "This is a preceding paragraph.\n\n"
        "- **field Mark:** This is the body text for Mark.\n"
        "- **field Peter:** \n"
        "- **field:** This guy has no name, it seems. Still, it should work.\n"
        "- **author:** Author McAuthorface\n"
        "- **year:** 2026\n"
        "- **publisher:** Self-published\n\n"
        "This is a follow-up paragraph.\n\n"
    )
    assert output == expected


def test_parse_docstring_no_mixed_field_lists() -> None:
    """Assert mixing normal fields with parameter fields is prohibited."""
    cfg = config.MinidocConfig()
    rst_str = (
        "This is the last paragraph of the docstring.\n\n"
        ":param a: This is a description of parameter ``a``.\n"
        ":field unsupported: This should cause trouble.\n"
        ":author: Troublemaker McAuthorface\n"
        ":return: A series of return values."
    )
    with pytest.raises(parsing.MixedFieldListError):
        parsing.parse_docstring(rst_str, cfg)


def test_parse_docstring_param_field_list_multiple_returns() -> None:
    """Test behavior when :returns: is given more than once."""
    cfg = config.MinidocConfig()
    rst_str = (
        "This is the last paragraph of the docstring.\n\n"
        ":param a: This is a description of parameter ``a``.\n"
        ":return: A series of return values.\n"
        ":returns: Another note is that the values are important."
    )
    output = parsing.parse_docstring(rst_str, cfg)
    # current behavior: simply concatenate
    expected = (
        "This is the last paragraph of the docstring.\n\n"
        "**Parameters:**\n\n"
        "- `a`: This is a description of parameter `a`.\n\n"
        "**Returns:**\n\nA series of return values.\n"
        "Another note is that the values are important.\n\n"
    )
    assert output == expected


# == SPHINX-STYLE ROLES ================================================
def test_parse_docstring_math_inline() -> None:
    """Test parsing inline math."""
    default_config = config.MinidocConfig()
    rst_str = "This text contains math: :math:`\\lambda = 2`."
    output = parsing.parse_docstring(rst_str, default_config)
    expected = "This text contains math: $\\lambda = 2$.\n\n"
    assert output == expected


def test_parse_docstring_math_block() -> None:
    """Test parsing a math block."""
    default_config = config.MinidocConfig()
    rst_str = (
        "This is a preceding paragraph.\n\n"
        ".. math::\n\n"
        "    \\lambda = x^2 - \\sqrt{2} y\n\n"
        "This is a closing paragraph."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    expected = (
        "This is a preceding paragraph.\n\n"
        "$$\n"
        "\\lambda = x^2 - \\sqrt{2} y\n"
        "$$\n\n"
        "This is a closing paragraph.\n\n"
    )
    assert output == expected


def test_parse_docstring_code_inline() -> None:
    """Test parsing inline code."""
    default_config = config.MinidocConfig()
    rst_str = "This text contains :code:`inline code`."
    output = parsing.parse_docstring(rst_str, default_config)
    expected = "This text contains `inline code`.\n\n"
    assert output == expected


def test_parse_docstring_code_block_no_language() -> None:
    """Test parsing a code block without specified language."""
    default_config = config.MinidocConfig()
    expected = (
        "This is a preceding paragraph.\n\n"
        "```\n"
        "pip install minidoc-md\n"
        "```\n\n"
        "This is a closing paragraph.\n\n"
    )

    # rst standard directive
    rst_str = (
        "This is a preceding paragraph.\n\n"
        ".. code::\n\n"
        "    pip install minidoc-md\n\n"
        "This is a closing paragraph."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    assert output == expected

    # Sphinx-specific directive
    rst_str = (
        "This is a preceding paragraph.\n\n"
        ".. code-block::\n\n"
        "    pip install minidoc-md\n\n"
        "This is a closing paragraph."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    assert output == expected


def test_parse_docstring_code_block_with_language() -> None:
    """Test parsing a code block with a specified language."""
    default_config = config.MinidocConfig()
    expected = (
        "This is a preceding paragraph.\n\n"
        "```Python\n"
        "import numpy as np\n"
        "```\n\n"
        "This is a closing paragraph.\n\n"
    )

    # rst standard directive
    rst_str = (
        "This is a preceding paragraph.\n\n"
        ".. code:: Python\n\n"
        "    import numpy as np\n\n"
        "This is a closing paragraph."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    assert output == expected

    # Sphinx-specific directive
    rst_str = (
        "This is a preceding paragraph.\n\n"
        ".. code-block:: Python\n\n"
        "    import numpy as np\n\n"
        "This is a closing paragraph."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    assert output == expected


_SPHINX_ROLES = [
    "mod",
    "func",
    "deco",
    "data",
    "const",
    "class",
    "meth",
    "attr",
    "type",
    "exc",
    "obj",
]


@pytest.mark.parametrize("role", _SPHINX_ROLES)
def test_parse_docstring_sphinx_role_simple(role: str) -> None:
    """Test parsing a simple sphinx role."""
    default_config = config.MinidocConfig()
    rst_str = f"This text contains a Sphinx ref (:{role}:`target_name`)."
    output = parsing.parse_docstring(rst_str, default_config)
    expected = "This text contains a Sphinx ref ([`target_name`](#target-name)).\n\n"
    assert output == expected


@pytest.mark.parametrize("role", _SPHINX_ROLES)
def test_parse_docstring_sphinx_role_path(role: str) -> None:
    """Test parsing a sphinx role with a full target path."""
    default_config = config.MinidocConfig()
    rst_str = (
        f"This text contains a Sphinx ref (:{role}:`my_module.submodule.target_name`)."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    expected = (
        "This text contains a Sphinx ref ([`my_module.submodule.target_name`]"
        "(#target-name)).\n\n"
    )
    assert output == expected


@pytest.mark.parametrize("role", _SPHINX_ROLES)
def test_parse_docstring_sphinx_role_shorthand(role: str) -> None:
    """Test parsing a sphinx role with a path, but shown shortened."""
    default_config = config.MinidocConfig()
    rst_str = (
        f"This text contains a Sphinx ref (:{role}:`~my_module.submodule.target_name`)."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    expected = "This text contains a Sphinx ref ([`target_name`](#target-name)).\n\n"
    assert output == expected


@pytest.mark.parametrize("role", _SPHINX_ROLES)
def test_parse_docstring_sphinx_disable_reference(role: str) -> None:
    """Test parsing a sphinx role which disables reference."""
    default_config = config.MinidocConfig()

    # simple reference
    rst_str = f"This text contains a Sphinx ref (:{role}:`!target_name`)."
    output = parsing.parse_docstring(rst_str, default_config)
    expected = "This text contains a Sphinx ref ([`target_name`](#)).\n\n"
    assert output == expected

    # full path
    rst_str = (
        f"This text contains a Sphinx ref (:{role}:`!my_module.submodule.target_name`)."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    expected = (
        "This text contains a Sphinx ref ([`my_module.submodule.target_name`](#)).\n\n"
    )
    assert output == expected


def test_parse_docstring_version_added() -> None:
    """Test parsing a text block with a "version added" directive."""
    default_config = config.MinidocConfig()
    expected = (
        "This is a preceding paragraph.\n\n"
        "> :heavy_plus_sign: Added in version 1.0.0: This is the feature "
        "that was added.\n\n"
        "> :heavy_plus_sign: Added in version 2.0.0\n\n"
        "This is a closing paragraph.\n\n"
    )

    # old version
    rst_str = (
        "This is a preceding paragraph.\n\n"
        ".. versionadded:: 1.0.0\n\n"
        "    This is the feature that was added.\n\n"
        ".. versionadded:: 2.0.0\n\n"
        "This is a closing paragraph."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    assert output == expected

    # new version
    rst_str = (
        "This is a preceding paragraph.\n\n"
        ".. version-added:: 1.0.0\n\n"
        "    This is the feature that was added.\n\n"
        ".. version-added:: 2.0.0\n\n"
        "This is a closing paragraph."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    assert output == expected


def test_parse_docstring_version_changed() -> None:
    """Test parsing a text block with a "version changed" directive."""
    default_config = config.MinidocConfig()
    expected = (
        "This is a preceding paragraph.\n\n"
        "> :recycle: Changed in version 1.0.0: This is the feature "
        "that was changed.\n\n"
        "> :recycle: Changed in version 2.0.0\n\n"
        "This is a closing paragraph.\n\n"
    )

    # old version
    rst_str = (
        "This is a preceding paragraph.\n\n"
        ".. versionchanged:: 1.0.0\n\n"
        "    This is the feature that was changed.\n\n"
        ".. versionchanged:: 2.0.0\n\n"
        "This is a closing paragraph."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    assert output == expected

    # new version
    rst_str = (
        "This is a preceding paragraph.\n\n"
        ".. version-changed:: 1.0.0\n\n"
        "    This is the feature that was changed.\n\n"
        ".. version-changed:: 2.0.0\n\n"
        "This is a closing paragraph."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    assert output == expected


def test_parse_docstring_version_deprecated() -> None:
    """Test parsing a text block with a "deprecated" directive."""
    default_config = config.MinidocConfig()
    expected = (
        "This is a preceding paragraph.\n\n"
        "> :warning: Deprecated since version 1.0.0: This is the feature "
        "that was deprecated.\n\n"
        "> :warning: Deprecated since version 2.0.0\n\n"
        "This is a closing paragraph.\n\n"
    )

    # old version
    rst_str = (
        "This is a preceding paragraph.\n\n"
        ".. deprecated:: 1.0.0\n\n"
        "    This is the feature that was deprecated.\n\n"
        ".. deprecated:: 2.0.0\n\n"
        "This is a closing paragraph."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    assert output == expected

    # new version
    rst_str = (
        "This is a preceding paragraph.\n\n"
        ".. version-deprecated:: 1.0.0\n\n"
        "    This is the feature that was deprecated.\n\n"
        ".. version-deprecated:: 2.0.0\n\n"
        "This is a closing paragraph."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    assert output == expected


def test_parse_docstring_version_removed() -> None:
    """Test parsing a text block with a "version removed" directive."""
    default_config = config.MinidocConfig()
    expected = (
        "This is a preceding paragraph.\n\n"
        "> :x: Removed in version 1.0.0: This is the feature "
        "that was removed.\n\n"
        "> :x: Removed in version 2.0.0\n\n"
        "This is a closing paragraph.\n\n"
    )

    # old version
    rst_str = (
        "This is a preceding paragraph.\n\n"
        ".. versionremoved:: 1.0.0\n\n"
        "    This is the feature that was removed.\n\n"
        ".. versionremoved:: 2.0.0\n\n"
        "This is a closing paragraph."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    assert output == expected

    # new version
    rst_str = (
        "This is a preceding paragraph.\n\n"
        ".. version-removed:: 1.0.0\n\n"
        "    This is the feature that was removed.\n\n"
        ".. version-removed:: 2.0.0\n\n"
        "This is a closing paragraph."
    )
    output = parsing.parse_docstring(rst_str, default_config)
    assert output == expected


# == NESTED BLOCKS =====================================================
# TODO: mixing of block quotes, field lists and lists


# == FULL DOCSTRING ====================================================
def test_parse_docstring(mock_docstring: str, expected_output_base: str) -> None:
    """Test the parsing function with the default config."""
    default_config = config.MinidocConfig()
    output = parsing.parse_docstring(mock_docstring, default_config)
    print(output)
    assert isinstance(output, str)
    assert output == expected_output_base
