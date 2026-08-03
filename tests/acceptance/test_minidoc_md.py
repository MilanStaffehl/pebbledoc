"""Acceptance tests for minidoc-md."""

import argparse
import difflib
from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from minidoc_md import cli


@pytest.fixture
def patch_open(mocker: MockerFixture) -> Mock:
    """Patch opening files to intercept final write of MD document."""
    patched_open = mocker.mock_open()
    mocker.patch("minidoc_md.cli.open", patched_open)
    return patched_open


def _prepare_namespace(
    source_directory: str | None = None,
    output: str = "API.md",
    admonition_style: str = "mix",
    title: str | None = None,
    no_module_docstring: bool = False,
    no_include_constants: bool = False,
    no_toc: bool = False,
    no_back_to_top: bool = False,
) -> argparse.Namespace:
    """
    Create a namespace with the attributes that minidoc expects.

    This function basically takes over the role of the user giving the
    application command line arguments. It takes all arguments and passes
    them on to a blank namespace object as-is, which is then returned.
    The parameter defaults are identical to that of the CLI.
    """
    return argparse.Namespace(package="stellarium_lite", **locals())


def assert_write_call(
    mock_write: Mock, output_file: str, expected: str
) -> None:
    """Check that the call to write contained the expected string."""
    # check everything worked
    mock_write.assert_called_once_with(Path(output_file), "w")
    handle = mock_write()
    handle.write.assert_called_once()
    assert handle.write.call_count == 1

    # check contents
    actual = handle.write.call_args[0][0]
    if not actual == expected:
        lines_actual = actual.splitlines(keepends=True)
        lines_expected = expected.splitlines(keepends=True)
        diff = difflib.unified_diff(lines_expected, lines_actual)
        msg = (
            f"Output was not identical to expected Markdown:\n\n"
            f"{''.join(diff)}"
        )
        pytest.fail(msg)


# == TEST CASES ========================================================


def test_minidoc_md_default_setup(patch_open: Mock) -> None:
    """Test minidoc-md with the default setup."""
    input_file = Path(__file__).parent / "expected" / "base.md"
    with open(input_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = _prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources")
    )
    exit_code = cli.handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected + "\n")
    assert exit_code == 0


def test_minidoc_md_different_name(patch_open: Mock) -> None:
    """Test giving a different file name."""
    input_file = Path(__file__).parent / "expected" / "base.md"
    with open(input_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = _prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        output="DOCUMENTATION.md",
    )
    exit_code = cli.handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected + "\n")
    assert exit_code == 0


@pytest.mark.parametrize(
    "admonition_style", ["github", "classic", "mix", "map"]
)
def test_minidoc_md_admonition_style(
    admonition_style: str, patch_open: Mock
) -> None:
    """Test minidoc-md for all admonition styles."""
    filename = f"admonitions_{admonition_style}.md"
    input_file = Path(__file__).parent / "expected" / filename
    with open(input_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = _prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        admonition_style=admonition_style,
    )
    exit_code = cli.handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected + "\n")
    assert exit_code == 0


def test_minidoc_md_custom_title(patch_open: Mock) -> None:
    """Test minidoc-md with a custom document title."""
    input_file = Path(__file__).parent / "expected" / "custom_title.md"
    with open(input_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = _prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        title="Custom documentation title",
    )
    exit_code = cli.handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected + "\n")
    assert exit_code == 0


def test_minidoc_md_no_module_docstring(patch_open: Mock) -> None:
    """Test minidoc-md when not using module docstrings."""
    filename = "no_module_docstring.md"
    input_file = Path(__file__).parent / "expected" / filename
    with open(input_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = _prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        no_module_docstring=True,
    )
    exit_code = cli.handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected + "\n")
    assert exit_code == 0


def test_minidoc_md_no_include_constants(patch_open: Mock) -> None:
    """Test minidoc-md when excluding constants."""
    input_file = Path(__file__).parent / "expected" / "no_constants.md"
    with open(input_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = _prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        no_include_constants=True,
    )
    exit_code = cli.handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected + "\n")
    assert exit_code == 0


def test_minidoc_md_no_toc(patch_open: Mock) -> None:
    """Test minidoc-md without a table of contents."""
    input_file = Path(__file__).parent / "expected" / "no_toc.md"
    with open(input_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = _prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        no_toc=True,
    )
    exit_code = cli.handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected + "\n")
    assert exit_code == 0


def test_minidoc_md_no_back_to_top(patch_open: Mock) -> None:
    """Test minidoc-md when excluding "back to top" links."""
    input_file = Path(__file__).parent / "expected" / "no_back_to_top.md"
    with open(input_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = _prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        no_back_to_top=True,
    )
    exit_code = cli.handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected + "\n")
    assert exit_code == 0


# == TESTS FOR INVALID INPUTS ==========================================
