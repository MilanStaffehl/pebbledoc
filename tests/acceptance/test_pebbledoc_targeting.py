"""Acceptance tests for targeting sections in existing files."""

import codecs
import difflib
import re
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


def assert_diff_matches(
    patched_open: Mock, output_file: Path, captured_diff: str
) -> None:
    """Check that the diff captured by capsys matches the expected diff."""
    patched_open.assert_called_once_with(output_file, "r")
    handle = patched_open()
    handle.write.assert_not_called()

    # Python escapes the backslashes of the ANSI sequences when we load
    # the expected diff from file, so we must decode the string again:
    diff_file = (
        Path(__file__).parent / "expected/diffs/expected_diff_targeting.txt"
    )
    encoded = diff_file.read_text().encode("utf-8")
    expected_diff = codecs.escape_decode(encoded)[0].decode("utf-8")
    # unfortunately, newlines in the captured output contain whitespace,
    # which multiple linting tools and IDEs remove from the text file
    # from which we load the expected diff. We therefore remove these
    # whitespaces before comparison:
    pattern = re.compile(r"^\s+\n", flags=re.MULTILINE)
    cleaned_diff = pattern.sub("\n", captured_diff)
    assert cleaned_diff == expected_diff


# == TEST CASES ========================================================


def test_pebbledoc_targeting_default_setup(
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


def test_pebbledoc_targeting_max_diff(
    mocker: MockerFixture, patch_config_discovery: None
) -> None:
    """Test pebbledoc with all config values changed."""
    output_file = Path(__file__).parent / "resources/mock_readme.md"
    with open(output_file, "r") as f:
        old_content = f.read()

    patched_open = mocker.mock_open(read_data=old_content)
    mocker.patch("pebbledoc.cli_logic.open", patched_open)

    expected_file = (
        Path(__file__).parent / "expected/targeting/targeting_max_diff.md"
    )
    with open(expected_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        output=str(output_file),
        target="Package Documentation",
        admonition_style="classic",
        main_docstring="omit",
        no_generic_intro=True,
        no_module_docstrings=True,
        no_include_constants=True,
        no_back_to_top=True,
        no_main_module_header=True,
        no_collapsible_params=True,
        no_references=True,
        no_preserve_linewraps=True,
    )
    exit_code = cli_logic._handle_args(namespace)

    assert_write_call(patched_open, namespace.output, expected + "\n")
    assert exit_code == cli_logic._ErrorCodes.EX_SUCCESS


def test_pebbledoc_targeting_overwrite_previous_content(
    mocker: MockerFixture, patch_config_discovery: None
) -> None:
    """Test pebbledoc with an existing insertion."""
    output_file = Path(__file__).parent / "resources/mock_readme_updated.md"
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


def test_pebbledoc_targeting_different_header_level(
    mocker: MockerFixture, patch_config_discovery: None
) -> None:
    """Test pebbledoc with a different target header level."""
    output_file = (
        Path(__file__).parent / "resources/mock_readme_different_level.md"
    )
    with open(output_file, "r") as f:
        old_content = f.read()

    patched_open = mocker.mock_open(read_data=old_content)
    mocker.patch("pebbledoc.cli_logic.open", patched_open)

    expected_file = (
        Path(__file__).parent
        / "expected/targeting/targeting_different_level.md"
    )
    with open(expected_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        output=str(output_file),
        target="Documentation (full API)",
    )
    exit_code = cli_logic._handle_args(namespace)

    assert_write_call(patched_open, namespace.output, expected + "\n")
    assert exit_code == cli_logic._ErrorCodes.EX_SUCCESS


def test_pebbledoc_targeting_inserting_at_end_of_file(
    mocker: MockerFixture, patch_config_discovery: None
) -> None:
    """Test that choosing a section at the EOF works."""
    output_file = Path(__file__).parent / "resources/mock_readme_eof.md"
    with open(output_file, "r") as f:
        old_content = f.read()

    patched_open = mocker.mock_open(read_data=old_content)
    mocker.patch("pebbledoc.cli_logic.open", patched_open)

    expected_file = (
        Path(__file__).parent / "expected/targeting/targeting_end_of_file.md"
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


def test_pebbledoc_targeting_overwriting_at_end_of_file(
    mocker: MockerFixture, patch_config_discovery: None
) -> None:
    """Test that overwriting an existing section at the EOF works."""
    output_file = (
        Path(__file__).parent / "resources/mock_readme_eof_updated.md"
    )
    with open(output_file, "r") as f:
        old_content = f.read()

    patched_open = mocker.mock_open(read_data=old_content)
    mocker.patch("pebbledoc.cli_logic.open", patched_open)

    expected_file = (
        Path(__file__).parent / "expected/targeting/targeting_end_of_file.md"
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


@pytest.mark.parametrize("short_names", [True, False])
def test_pebbledoc_targeting_no_toc(
    short_names: bool, mocker: MockerFixture, patch_config_discovery: None
) -> None:
    """Test that the options regarding the TOC have no effect."""
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
        no_toc=True,
        no_full_toc_name=short_names,
    )
    exit_code = cli_logic._handle_args(namespace)

    assert_write_call(patched_open, namespace.output, expected + "\n")
    assert exit_code == cli_logic._ErrorCodes.EX_SUCCESS


def test_pebbledoc_targeting_custom_title(
    mocker: MockerFixture, patch_config_discovery: None
) -> None:
    """Test that the option to set a custom title has no effect."""
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
        title="I should absolutely not show up!",
    )
    exit_code = cli_logic._handle_args(namespace)

    assert_write_call(patched_open, namespace.output, expected + "\n")
    assert exit_code == cli_logic._ErrorCodes.EX_SUCCESS


@pytest.mark.parametrize("position", ["pre", "post"])
def test_pebbledoc_targeting_main_docstring(
    position: str, mocker: MockerFixture, patch_config_discovery: None
) -> None:
    """Test that the options ``pre`` and ``post`` are identical."""
    output_file = Path(__file__).parent / "resources/mock_readme.md"
    with open(output_file, "r") as f:
        old_content = f.read()

    patched_open = mocker.mock_open(read_data=old_content)
    mocker.patch("pebbledoc.cli_logic.open", patched_open)

    expected_file = (
        Path(__file__).parent
        / "expected/targeting/targeting_main_docstring_pre_post.md"
    )
    with open(expected_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        output=str(output_file),
        target="Package Documentation",
        main_docstring=position,
    )
    exit_code = cli_logic._handle_args(namespace)

    assert_write_call(patched_open, namespace.output, expected + "\n")
    assert exit_code == cli_logic._ErrorCodes.EX_SUCCESS


# == DIFF TEST CASES ===================================================


def test_pebbledoc_targeting_diff_option(
    capsys: pytest.CaptureFixture,
    mocker: MockerFixture,
    patch_config_discovery: None,
) -> None:
    """Test ``--diff`` when there are some changes."""
    output_file = Path(__file__).parent / "resources/mock_readme_diff.md"
    with open(output_file, "r") as f:
        old_content = f.read()

    patched_open = mocker.mock_open(read_data=old_content)
    mocker.patch("pebbledoc.cli_logic.open", patched_open)

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        package="bootes_loader",
        source_directory=str(Path(__file__).parent / "resources"),
        output=str(output_file),
        target="Package Documentation",
        diff=True,
    )
    exit_code = cli_logic._handle_args(namespace)

    assert patched_open.call_count == 1  # one read, no write!
    assert_diff_matches(patched_open, output_file, capsys.readouterr().out)
    assert exit_code == cli_logic._ErrorCodes.EX_SUCCESS


def test_pebbledoc_targeting_diff_option_no_diff(
    capsys: pytest.CaptureFixture,
    mocker: MockerFixture,
    patch_config_discovery: None,
) -> None:
    """Test ``--diff`` when there are no changes to report."""
    output_file = (
        Path(__file__).parent / "resources/mock_readme_diff_no_changes.md"
    )
    with open(output_file, "r") as f:
        old_content = f.read()

    patched_open = mocker.mock_open(read_data=old_content)
    mocker.patch("pebbledoc.cli_logic.open", patched_open)

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        package="bootes_loader",
        source_directory=str(Path(__file__).parent / "resources"),
        output=str(output_file),
        target="Package Documentation",
        diff=True,
    )
    exit_code = cli_logic._handle_args(namespace)

    assert exit_code == cli_logic._ErrorCodes.EX_SUCCESS
    patched_open.assert_called_once_with(output_file, "r")
    handle = patched_open()
    handle.write.assert_not_called()

    assert capsys.readouterr().out == ""  # no diff


def test_pebbledoc_targeting_diff_option_with_exit_code(
    capsys: pytest.CaptureFixture,
    mocker: MockerFixture,
    patch_config_discovery: None,
) -> None:
    """Test ``--diff`` option with ``--exit-code``."""
    output_file = Path(__file__).parent / "resources/mock_readme_diff.md"
    with open(output_file, "r") as f:
        old_content = f.read()

    patched_open = mocker.mock_open(read_data=old_content)
    mocker.patch("pebbledoc.cli_logic.open", patched_open)

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        package="bootes_loader",
        source_directory=str(Path(__file__).parent / "resources"),
        output=str(output_file),
        target="Package Documentation",
        diff=True,
        exit_code=True,
    )
    exit_code = cli_logic._handle_args(namespace)

    assert patched_open.call_count == 1  # one read, no write!
    assert_diff_matches(patched_open, output_file, capsys.readouterr().out)
    assert exit_code == cli_logic._ErrorCodes.EX_DOCS_CHANGED
