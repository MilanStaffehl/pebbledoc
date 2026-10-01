"""Acceptance tests for building docs from templates."""

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


def assert_diff_matches(
    patched_open: Mock, output_file: Path, captured_diff: str, diff_file: Path
) -> None:
    """Check that the diff captured by capsys matches the expected diff."""
    patched_open.assert_called_once_with(output_file, "r")
    handle = patched_open()
    handle.write.assert_not_called()

    # Python escapes the backslashes of the ANSI sequences when we load
    # the expected diff from file, so we must decode the string again:
    encoded = diff_file.read_text().encode("utf-8")
    expected_diff = codecs.escape_decode(encoded)[0].decode("utf-8")
    # unfortunately, newlines in the captured output contain whitespace,
    # which multiple linting tools and IDEs remove from the text file
    # from which we load the expected diff. We therefore remove these
    # whitespaces before comparison:
    pattern = re.compile(r"^\s+\n", flags=re.MULTILINE)
    cleaned_diff = pattern.sub("\n", captured_diff)
    # unfortunately our last diff has as context line a newline, which
    # IDEs remove from the expected diff file, so we add it back in here:
    assert cleaned_diff == expected_diff + "\n"


# == TEST CASES ========================================================


def test_pebbledoc_templating_default_setup(
    patch_open: Mock, patch_config_discovery: None
) -> None:
    """Test pebbledoc templates with the default setup."""
    template_file = Path(__file__).parent / "resources/mock_template.md"
    expected_file = (
        Path(__file__).parent / "expected/templating/templating_base.md"
    )
    with open(expected_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        template=str(template_file),
    )
    exit_code = cli_logic._handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected)
    assert exit_code == cli_logic._ErrorCodes.EX_SUCCESS


def test_pebbledoc_templating_max_diff(
    patch_open: Mock, patch_config_discovery: None
) -> None:
    """Test pebbledoc templates with all config values changed."""
    template_file = Path(__file__).parent / "resources/mock_template.md"
    expected_file = (
        Path(__file__).parent / "expected/templating/templating_max_diff.md"
    )
    with open(expected_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        output="STARTING_GUIDE.md",
        template=str(template_file),
        admonition_style="classic",
        main_docstring="omit",
        title="I will be overwritten",
        no_generic_intro=True,  # should have no effect
        no_module_docstrings=True,  # should have no effect
        no_include_constants=True,
        no_toc=True,  # should have no effect
        no_back_to_top=True,
        no_main_module_header=True,
        no_collapsible_params=True,
        no_references=True,
        no_preserve_linewraps=True,
    )
    exit_code = cli_logic._handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected)
    assert exit_code == cli_logic._ErrorCodes.EX_SUCCESS


def test_pebbledoc_templating_excluded_members(
    patch_open: Mock, patch_config_discovery: None
) -> None:
    """Test that excluded members are not in template sections."""
    template_file = Path(__file__).parent / "resources/mock_template.md"
    expected_file = (
        Path(__file__).parent / "expected/templating/templating_exclude.md"
    )
    with open(expected_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    exclude_list = [
        "stellarium_lite.observation.ObservableMixin",
        "stellarium_lite.observation.VariableStar",
        "stellarium_lite.observation.HybridObject",
    ]
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        template=str(template_file),
        exclude=exclude_list,
    )
    exit_code = cli_logic._handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected)
    assert exit_code == cli_logic._ErrorCodes.EX_SUCCESS


def test_pebbledoc_templating_excluded_members_directives(
    patch_open: Mock, patch_config_discovery: None
) -> None:
    """Test behavior when an excluded member is requested in a directive."""
    # i.e.: what if a member is excluded, but a directive requests only
    # this one member, without its children?
    template_file = Path(__file__).parent / "resources/mock_template.md"
    expected_file = (
        Path(__file__).parent
        / "expected/templating/templating_exclude_requested.md"
    )
    with open(expected_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    exclude_list = [
        "stellarium_lite.load_catalog",
    ]
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        template=str(template_file),
        exclude=exclude_list,
    )
    exit_code = cli_logic._handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected)
    assert exit_code == cli_logic._ErrorCodes.EX_SUCCESS


# == SPECIAL TESTS =====================================================


def test_pebbledoc_templating_exit_code(
    patch_open: Mock, patch_config_discovery: None
) -> None:
    """Test pebbledoc emits non-zero exit code on change when instructed."""
    template_file = Path(__file__).parent / "resources/mock_template.md"
    expected_file = (
        Path(__file__).parent / "expected/templating/templating_base.md"
    )
    with open(expected_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        template=str(template_file),
        exit_code=True,
    )
    exit_code = cli_logic._handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected)
    assert exit_code == cli_logic._ErrorCodes.EX_DOCS_CHANGED


def test_pebbledoc_templating_and_targeting(
    patch_open: Mock, patch_config_discovery: None
) -> None:
    """Test that providing target and template causes an error."""
    template_file = Path(__file__).parent / "resources/mock_template.md"

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        template=str(template_file),
        target="Getting started",
    )
    exit_code = cli_logic._handle_args(namespace)
    patch_open.assert_not_called()
    assert exit_code == cli_logic._ErrorCodes.EX_BAD_ARGS


# == DIFF TEST CASES ===================================================


def test_pebbledoc_templating_diff_option(
    capsys: pytest.CaptureFixture,
    mocker: MockerFixture,
    patch_config_discovery: None,
) -> None:
    """Test ``--diff`` when there are some changes."""
    template_file = Path(__file__).parent / "resources/mock_template.md"
    output_file = Path(__file__).parent / "resources/mock_template_diff.md"
    with open(output_file, "r") as f:
        old_content = f.read()

    patched_open = mocker.mock_open(read_data=old_content)
    mocker.patch("pebbledoc.cli_logic.open", patched_open)

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        template=str(template_file),
        output=str(output_file),
        diff=True,
    )
    exit_code = cli_logic._handle_args(namespace)

    assert patched_open.call_count == 1  # one read, no write!
    diff_file = (
        Path(__file__).parent / "expected/diffs/expected_diff_templating.txt"
    )
    assert_diff_matches(
        patched_open, output_file, capsys.readouterr().out, diff_file
    )
    assert exit_code == cli_logic._ErrorCodes.EX_SUCCESS


@pytest.mark.parametrize("emit_exit_code", [True, False])
def test_pebbledoc_templating_diff_option_no_diff(
    emit_exit_code: bool,
    capsys: pytest.CaptureFixture,
    mocker: MockerFixture,
    patch_config_discovery: None,
) -> None:
    """Test ``--diff`` when there are no changes to report."""
    template_file = Path(__file__).parent / "resources/mock_template.md"
    output_file = (
        Path(__file__).parent / "expected/templating/templating_base.md"
    )
    with open(output_file, "r") as f:
        old_content = f.read()

    patched_open = mocker.mock_open(read_data=old_content)
    mocker.patch("pebbledoc.cli_logic.open", patched_open)

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        template=str(template_file),
        output=str(output_file),
        diff=True,
        exit_code=emit_exit_code,
    )
    exit_code = cli_logic._handle_args(namespace)

    assert patched_open.call_count == 1  # one read, no write!
    assert exit_code == cli_logic._ErrorCodes.EX_SUCCESS
    patched_open.assert_called_once_with(output_file, "r")
    handle = patched_open()
    handle.write.assert_not_called()

    assert capsys.readouterr().out == ""  # no diff


def test_pebbledoc_templating_diff_option_with_exit_code(
    capsys: pytest.CaptureFixture,
    mocker: MockerFixture,
    patch_config_discovery: None,
) -> None:
    """Test ``--diff`` option with ``--exit-code``."""
    template_file = Path(__file__).parent / "resources/mock_template.md"
    output_file = Path(__file__).parent / "resources/mock_template_diff.md"
    with open(output_file, "r") as f:
        old_content = f.read()

    patched_open = mocker.mock_open(read_data=old_content)
    mocker.patch("pebbledoc.cli_logic.open", patched_open)

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        template=str(template_file),
        output=str(output_file),
        diff=True,
        exit_code=True,
    )
    exit_code = cli_logic._handle_args(namespace)

    assert patched_open.call_count == 1  # one read, no write!
    diff_file = (
        Path(__file__).parent / "expected/diffs/expected_diff_templating.txt"
    )
    assert_diff_matches(
        patched_open, output_file, capsys.readouterr().out, diff_file
    )
    assert exit_code == cli_logic._ErrorCodes.EX_DOCS_CHANGED


def test_pebbledoc_templating_diff_unchanged_docs_changed_text(
    capsys: pytest.CaptureFixture,
    mocker: MockerFixture,
    patch_config_discovery: None,
) -> None:
    """Test ``--diff`` when docstrings are the same, but the template changed."""
    template_file = (
        Path(__file__).parent / "resources/mock_template_changed.md"
    )
    output_file = (
        Path(__file__).parent / "expected/templating/templating_base.md"
    )
    with open(output_file, "r") as f:
        old_content = f.read()

    patched_open = mocker.mock_open(read_data=old_content)
    mocker.patch("pebbledoc.cli_logic.open", patched_open)

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        template=str(template_file),
        output=str(output_file),
        diff=True,
    )
    exit_code = cli_logic._handle_args(namespace)

    assert patched_open.call_count == 1  # one read, no write!
    diff_file = (
        Path(__file__).parent
        / "expected/diffs/expected_diff_templating_changed.txt"
    )
    assert_diff_matches(
        patched_open, output_file, capsys.readouterr().out, diff_file
    )
    assert exit_code == cli_logic._ErrorCodes.EX_SUCCESS
