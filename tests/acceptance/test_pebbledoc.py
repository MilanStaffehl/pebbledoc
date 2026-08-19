"""Acceptance tests for pebbledoc."""

import difflib
import importlib
import sys
from pathlib import Path
from typing import Final
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from pebbledoc import cli

sys.path.insert(0, str(Path(__file__).parents[1]))
import utils

ERROR_PREFIX: Final[str] = "\033[91mError:\033[0m"


@pytest.fixture
def patch_open(mocker: MockerFixture) -> Mock:
    """Patch opening files to intercept final write of MD document."""
    patched_open = mocker.mock_open()
    mocker.patch("pebbledoc.cli.open", patched_open)
    return patched_open


@pytest.fixture
def patch_config_discovery(mocker: MockerFixture) -> None:
    """Prevent config file discovery from running."""
    mocker.patch("pebbledoc.config._discover_config_file", return_value=None)


@pytest.fixture
def patch_module_all(mocker: MockerFixture) -> None:
    """Path the stellarium_lite module to have no __all__."""
    sys.path.append(str(Path(__file__).parent / "resources"))
    package = importlib.import_module("stellarium_lite")
    mocker.patch.object(package, "__all__", None)
    sys.path.pop()


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
        diff = difflib.unified_diff(lines_expected, lines_actual)
        msg = (
            f"Output was not identical to expected Markdown:\n\n"
            f"{''.join(diff)}"
        )
        pytest.fail(msg)


# == TEST CASES ========================================================


def test_pebbledoc_default_setup(
    patch_open: Mock, patch_config_discovery: None
) -> None:
    """Test pebbledoc with the default setup."""
    input_file = Path(__file__).parent / "expected" / "base.md"
    with open(input_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources")
    )
    exit_code = cli._handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected + "\n")
    assert exit_code == 0


def test_pebbledoc_member_discovery(
    patch_open: Mock, patch_config_discovery: None, patch_module_all: None
) -> None:
    """Test pebbledoc when the package has no __all__"""
    input_file = Path(__file__).parent / "expected" / "from_ast_discovery.md"
    with open(input_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources")
    )
    exit_code = cli._handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected + "\n")
    assert exit_code == 0


def test_pebbledoc_different_name(
    patch_open: Mock, patch_config_discovery: None
) -> None:
    """Test giving a different file name."""
    input_file = Path(__file__).parent / "expected" / "base.md"
    with open(input_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        output="DOCUMENTATION.md",
    )
    exit_code = cli._handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected + "\n")
    assert exit_code == 0


@pytest.mark.parametrize(
    "admonition_style", ["github", "classic", "mix", "map"]
)
def test_pebbledoc_admonition_style(
    admonition_style: str, patch_open: Mock, patch_config_discovery: None
) -> None:
    """Test pebbledoc for all admonition styles."""
    filename = f"admonitions_{admonition_style}.md"
    input_file = Path(__file__).parent / "expected" / filename
    with open(input_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        admonition_style=admonition_style,
    )
    exit_code = cli._handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected + "\n")
    assert exit_code == 0


def test_pebbledoc_custom_title(
    patch_open: Mock, patch_config_discovery: None
) -> None:
    """Test pebbledoc with a custom document title."""
    input_file = Path(__file__).parent / "expected" / "custom_title.md"
    with open(input_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        title="Custom documentation title",
    )
    exit_code = cli._handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected + "\n")
    assert exit_code == 0


def test_pebbledoc_no_module_docstring(
    patch_open: Mock, patch_config_discovery: None
) -> None:
    """Test pebbledoc when not using module docstrings."""
    filename = "no_module_docstring.md"
    input_file = Path(__file__).parent / "expected" / filename
    with open(input_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        no_module_docstring=True,
    )
    exit_code = cli._handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected + "\n")
    assert exit_code == 0


def test_pebbledoc_no_include_constants(
    patch_open: Mock, patch_config_discovery: None
) -> None:
    """Test pebbledoc when excluding constants."""
    input_file = Path(__file__).parent / "expected" / "no_constants.md"
    with open(input_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        no_include_constants=True,
    )
    exit_code = cli._handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected + "\n")
    assert exit_code == 0


def test_pebbledoc_no_toc(
    patch_open: Mock, patch_config_discovery: None
) -> None:
    """Test pebbledoc without a table of contents."""
    input_file = Path(__file__).parent / "expected" / "no_toc.md"
    with open(input_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        no_toc=True,
    )
    exit_code = cli._handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected + "\n")
    assert exit_code == 0


def test_pebbledoc_no_back_to_top(
    patch_open: Mock, patch_config_discovery: None
) -> None:
    """Test pebbledoc when excluding "back to top" links."""
    input_file = Path(__file__).parent / "expected" / "no_back_to_top.md"
    with open(input_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        no_back_to_top=True,
    )
    exit_code = cli._handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected + "\n")
    assert exit_code == 0


def test_pebbledoc_no_main_module_header(
    patch_open: Mock, patch_config_discovery: None
) -> None:
    """Test pebbledoc when excluding the main module h2 header."""
    input_file = (
        Path(__file__).parent / "expected" / "no_main_module_header.md"
    )
    with open(input_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        no_main_module_header=True,
    )
    exit_code = cli._handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected + "\n")
    assert exit_code == 0


def test_pebbledoc_untyped_package(
    patch_open: Mock, patch_config_discovery: None
) -> None:
    """Test pebbledoc when type hints are only in docstrings."""
    input_file = (
        Path(__file__).parent / "expected" / "bootes_loader" / "base.md"
    )
    with open(input_file, "r") as f:
        expected = f.read()

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        package="bootes_loader",
        source_directory=str(Path(__file__).parent / "resources"),
    )
    exit_code = cli._handle_args(namespace)

    assert_write_call(patch_open, namespace.output, expected + "\n")
    assert exit_code == 0


def test_pebbledoc_config_file(
    mocker: MockerFixture, patch_config_discovery: None
) -> None:
    """Test pebbledoc when config file is used."""
    mock_pyproject = (
        b"[pebbledoc]\n"
        b'package_name = "stellarium_lite"\n'
        b'admonition_style = "classic"\n'
        b"include_back_to_top = false\n"
        b"include_toc = false\n"
    )
    m = mocker.mock_open(read_data=mock_pyproject)
    mock_open = mocker.patch("pebbledoc.config.open", m)
    m2 = mocker.mock_open()
    mock_write = mocker.patch("pebbledoc.cli.open", m2)
    # ensure the config file "exists"
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.is_file", return_value=True)

    input_file = Path(__file__).parent / "expected" / "from_config_file.md"
    with open(input_file, "r") as f:
        expected = f.read()
    expected += "\n"

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        config_file="pebbledoc.toml",
    )
    exit_code = cli._handle_args(namespace)

    mock_open.assert_called_once_with(
        Path("pebbledoc.toml").resolve(),
        "rb",
    )
    mock_write.assert_called_once_with(Path("API.md").resolve(), "w")
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
    assert exit_code == 0


def test_pebbledoc_config_file_with_output_renamed(
    mocker: MockerFixture, patch_config_discovery: None
) -> None:
    """Test pebbledoc when config file renames the output file."""
    mock_pyproject = (
        b"[pebbledoc]\n"
        b'package_name = "stellarium_lite"\n'
        b'output = "DOCUMENTATION.md"\n'
        b'admonition_style = "classic"\n'
        b"include_back_to_top = false\n"
        b"include_toc = false\n"
    )
    m = mocker.mock_open(read_data=mock_pyproject)
    mock_open = mocker.patch("pebbledoc.config.open", m)
    m2 = mocker.mock_open()
    mock_write = mocker.patch("pebbledoc.cli.open", m2)
    # ensure the config file "exists"
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.is_file", return_value=True)

    input_file = Path(__file__).parent / "expected" / "from_config_file.md"
    with open(input_file, "r") as f:
        expected = f.read()
    expected += "\n"

    # create a run config and execute the code
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        config_file="pebbledoc.toml",
    )
    exit_code = cli._handle_args(namespace)

    mock_open.assert_called_once_with(
        Path("pebbledoc.toml").resolve(),
        "rb",
    )
    mock_write.assert_called_once_with(
        Path("DOCUMENTATION.md").resolve(),
        "w",
    )
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
    assert exit_code == 0


# == TESTS FOR INVALID INPUTS ==========================================


def test_pebbledoc_invalid_output_file(
    patch_config_discovery: None, capsys: pytest.CaptureFixture
) -> None:
    """Test the behavior when given an invalid output file."""
    # output is a directory
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        output=str(Path(__file__).parent),  # dir, not a file
    )
    exit_code = cli._handle_args(namespace)

    out = capsys.readouterr()
    assert (
        out.err == f"{ERROR_PREFIX} Output must be a file, not a directory\n"
    )
    assert exit_code == 1

    # output directory does not exist
    output_path = Path("/this/does/not/exist/API.md")
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        output=str(output_path),
    )
    exit_code = cli._handle_args(namespace)

    out = capsys.readouterr()
    expected_msg = (
        f"{ERROR_PREFIX} Output directory {output_path.parent.resolve()} does "
        f"not exist\n"
    )
    assert out.err == expected_msg
    assert exit_code == 1


def test_pebbledoc_invalid_source_directory(
    patch_config_discovery: None, capsys: pytest.CaptureFixture
) -> None:
    """Test the behavior when given an invalid source directory."""
    # output is a directory
    source_dir = Path(__file__).parent / "nonexistent"
    namespace = utils.prepare_namespace(
        source_directory=str(source_dir),
    )
    exit_code = cli._handle_args(namespace)

    out = capsys.readouterr()
    expected_msg = (
        f"{ERROR_PREFIX} Source directory {source_dir} does not exist\n"
    )
    assert out.err == expected_msg
    assert exit_code == 1


def test_pebbledoc_import_error(
    patch_config_discovery: None, capsys: pytest.CaptureFixture
) -> None:
    """Test the behavior when given an unimportable package."""
    namespace = utils.prepare_namespace(
        package="makebelieve",
        source_directory=str(Path(__file__).parent / "resources"),
    )
    exit_code = cli._handle_args(namespace)

    out = capsys.readouterr()
    expected_msg = (
        f"{ERROR_PREFIX} Could not import package makebelieve or its "
        f"dependencies: No module named 'makebelieve'\n"
    )
    assert out.err == expected_msg
    assert exit_code == 2


def test_pebbledoc_unable_to_write_output(
    patch_config_discovery: None,
    capsys: pytest.CaptureFixture,
    mocker: MockerFixture,
) -> None:
    """Test the behavior when given an unimportable package."""
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
    )
    mocker.patch(
        "pebbledoc.cli.open",
        side_effect=PermissionError("Not allowed to write"),
    )
    exit_code = cli._handle_args(namespace)

    out = capsys.readouterr()
    output = Path("API.md").resolve()
    expected_msg = (
        f"{ERROR_PREFIX} Could not write {output}: Not allowed to write\n"
    )
    assert out.err == expected_msg
    assert exit_code == 3


def test_pebbledoc_invalid_config_file(
    capsys: pytest.CaptureFixture, mocker: MockerFixture
) -> None:
    """Test the behavior when given an unimportable package."""
    # invalid file path
    config_file = Path("nonexistent")
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        config_file=str(config_file),
    )
    exit_code = cli._handle_args(namespace)

    out = capsys.readouterr()
    expected_msg = (
        f"{ERROR_PREFIX} Could not locate config file: {config_file.resolve()} "
        f"is not a file or does not exist\n"
    )
    assert out.err == expected_msg
    assert exit_code == 4

    # wrong file format
    mocker.patch("pebbledoc.cli.Path.exists", return_value=True)
    mocker.patch("pebbledoc.cli.Path.is_file", return_value=True)
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
        config_file="myconfig.yaml",
    )
    exit_code = cli._handle_args(namespace)

    out = capsys.readouterr()
    expected_msg = (
        f"{ERROR_PREFIX} Could not locate config file: Config file must be "
        f"one of the following: pebbledoc.toml, .pebbledoc.toml, "
        f"pyproject.toml\n"
    )
    assert out.err == expected_msg
    assert exit_code == 4


def test_pebbledoc_no_package_origin(
    patch_config_discovery: None,
    patch_module_all: None,
    mocker: MockerFixture,
    capsys: pytest.CaptureFixture,
) -> None:
    """Test the behavior when the package has no defined origin."""
    # patch module __spec__ and __file__ - should rarely happen, but
    # we cover it in tests anyhow
    sys.path.append(str(Path(__file__).parent / "resources"))
    package = importlib.import_module("stellarium_lite")
    mocker.patch.object(package, "__spec__", None)
    mocker.patch.object(package, "__file__", None)
    sys.path.pop(0)

    # Attempt to load the package - no __all__ means public member discovery
    # will attempt to fall back to __spec__, then __file__, both of which
    # we have disabled. An error should occur.
    namespace = utils.prepare_namespace(
        source_directory=str(Path(__file__).parent / "resources"),
    )
    exit_code = cli._handle_args(namespace)

    out = capsys.readouterr()
    expected_msg = (
        f"{ERROR_PREFIX} One or more (sub-)packages could not be found: "
        f"Unable to find origin of module stellarium_lite\n"
    )
    assert out.err == expected_msg
    assert exit_code == 5
