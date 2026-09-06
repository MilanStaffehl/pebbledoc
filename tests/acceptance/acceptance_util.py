"""Utilities for acceptance tests."""

import difflib
from pathlib import Path
from unittest.mock import Mock

import pytest


def assert_write_call(
    mock_write: Mock, output_file: str | None, expected: str
) -> None:
    """Check that the call to write contained the expected string."""
    # check everything worked
    if output_file is None:
        output_file = "API.md"
    mock_write.assert_called_once_with(Path(output_file).resolve(), "w")
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
