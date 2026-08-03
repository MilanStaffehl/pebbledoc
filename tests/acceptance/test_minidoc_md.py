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
        diff = difflib.unified_diff(lines_actual, lines_expected)
        msg = (
            f"Output was not identical to expected Markdown:\n\n"
            f"{''.join(diff)}"
        )
        pytest.fail(msg)


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
