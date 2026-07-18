"""Tests for the parsing module."""

import inspect
from pathlib import Path

import pytest

from minidoc_md import config, parsing


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


def test_parse_docstring(mock_docstring: str, expected_output_base: str) -> None:
    """Test the parsing function with the default config."""
    default_config = config.MinidocConfig()
    output = parsing.parse_docstring(mock_docstring, default_config)
    assert isinstance(output, str)
    print(output)
    assert output == expected_output_base
