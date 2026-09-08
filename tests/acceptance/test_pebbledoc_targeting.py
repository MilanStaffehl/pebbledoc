"""Acceptance tests for targeting sections in existing files."""

import difflib
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from pebbledoc import cli_logic

sys.path.insert(0, str(Path(__file__).parents[1]))
import utils


def assert_write_call(
    mock_write: Mock, output_file: str | None, expected: str
) -> None:
    """Check that the call to write contained the expected string."""
    # check everything worked
    if output_file is None:
        output_file = "API.md"
    assert mock_write.call_count == 2  # one read, one write
    read_call = mock_write.call_args_list[0]
    assert read_call.args == (Path(output_file).resolve(), "r")
    write_call = mock_write.call_args_list[1]
    assert write_call.args == (Path(output_file).resolve(), "w")
    handle = mock_write()
    handle.write.assert_called_once()
    assert handle.write.call_count == 1

    # check contents
    actual = handle.write.call_args[0][0]
    if not actual == expected:
        lines_actual = actual.splitlines(keepends=True)
        lines_expected = expected.splitlines(keepends=True)
        diff = difflib.unified_diff(
            lines_expected, lines_actual, fromfile="expected", tofile="actual"
        )
        msg = (
            f"Output was not identical to expected Markdown:\n\n"
            f"{''.join(diff)}"
        )
        pytest.fail(msg)


def test_pebbledoc_default_setup(
    mocker: MockerFixture, patch_config_discovery: None
) -> None:
    """Test pebbledoc with the default setup."""
    output_file = Path(__file__).parent / "resources/mock_readme.md"
    with open(output_file, "r") as f:
        old_content = f.read()

    patched_open = mocker.mock_open(read_data=old_content)
    mocker.patch("pebbledoc.cli_logic.open", patched_open)

    expected_file = (
        Path(__file__).parent / "expected/targeting/targeting_base.md"
    )
    with open(expected_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        output=str(output_file),
        target="Package Documentation",
    )
    exit_code = cli_logic._handle_args(namespace)

    assert_write_call(patched_open, namespace.output, expected + "\n")
    assert exit_code == cli_logic._ErrorCodes.EX_SUCCESS
