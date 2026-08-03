"""Acceptance tests for minidoc-md."""

import argparse
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

    # check everything worked
    patch_open.assert_called_once_with(Path(namespace.output), "w")
    handle = patch_open()
    handle.write.assert_called_once_with(expected + "\n")
    assert exit_code == 0
