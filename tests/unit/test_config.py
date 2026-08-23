"""Tests for the CLI module."""

import sys
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pebbledoc import cli, config

sys.path.insert(0, str(Path(__file__).parents[1]))
import utils


def assert_config(
    cfg: config.PebbledocConfig,
    *,
    package: str = "test_package",
    source_directory: str | None = None,
    output: str = "API.md",
    exclude: list[str] | None = None,
    admonition_style: str = "mix",
    document_title: str | None = None,
    document_constants: bool = True,
    module_docstring: bool = True,
    include_toc: bool = True,
    include_back_to_top: bool = True,
    main_module_header: bool = True,
    collapsible_params: bool = True,
    reference_links: bool = True,
    full_toc_name: bool = True,
) -> None:
    """Check that the given config has the expected values."""
    if exclude is None:
        exclude = []
    assert cfg.package_name == package
    assert cfg.source_directory == source_directory
    assert cfg.output == output
    assert cfg.exclude == exclude
    assert cfg.admonition_style == admonition_style
    assert cfg.document_title == document_title
    assert cfg.document_constants is document_constants
    assert cfg.module_docstring is module_docstring
    assert cfg.include_toc is include_toc
    assert cfg.include_back_to_top is include_back_to_top
    assert cfg.main_module_header is main_module_header
    assert cfg.collapsible_params is collapsible_params
    assert cfg.reference_links is reference_links
    assert cfg.full_toc_name is full_toc_name


def test_build_config_default() -> None:
    """Test building a config with no args."""
    namespace = utils.prepare_namespace(package="test_package")
    output = cli.build_config(namespace)
    assert_config(output)  # default values should be set


def test_build_config_max_diff() -> None:
    """Test building a config with every argument is changed from default."""
    namespace = utils.prepare_namespace(
        package="test_package",
        source_directory="~/pylibs/my_package",
        output="~/Documents/docs/DOCUMENTATION.md",
        exclude=["my_func, MyClass"],
        admonition_style="github",
        title="My custom title",
        no_module_docstring=True,
        no_include_constants=True,
        no_toc=True,
        no_back_to_top=True,
        no_main_module_header=True,
        no_collapsible_params=True,
        no_references=True,
        no_full_toc_name=True,
    )
    output = cli.build_config(namespace)
    assert_config(
        output,
        package="test_package",
        source_directory="~/pylibs/my_package",
        output="~/Documents/docs/DOCUMENTATION.md",
        exclude=["my_func, MyClass"],
        admonition_style="github",
        document_title="My custom title",
        module_docstring=False,
        document_constants=False,
        include_toc=False,
        include_back_to_top=False,
        main_module_header=False,
        collapsible_params=False,
        reference_links=False,
        full_toc_name=False,
    )


def test_build_config_cli_args() -> None:
    """Test building a config when CLI args are given."""
    mock_source_dir = "~/pylibs/my_package"
    namespace = utils.prepare_namespace(
        package="test_package",
        source_directory=mock_source_dir,
        output="~/Documents/docs/DOCUMENTATION.md",
        exclude=["my_func, MyClass"],
        admonition_style="github",
        title="My custom title",
        no_include_constants=True,
        no_module_docstring=True,
    )
    output = cli.build_config(namespace)
    assert_config(
        output,
        source_directory=mock_source_dir,
        output="~/Documents/docs/DOCUMENTATION.md",
        exclude=["my_func, MyClass"],
        admonition_style="github",
        document_title="My custom title",
        document_constants=False,
        module_docstring=False,
    )


def test_build_config_pyrpoject(mocker: MockerFixture) -> None:
    """Test building a config when defaults are in a pyproject.toml."""
    mock_pyproject = (
        b"[tool.pebbledoc]\n"
        b'source_directory = "~/pylibs/my_package"\n'
        b'package_name = "test_package"\n'
        b'exclude = ["my_func, MyClass"]\n'
        b'admonition_style = "classic"\n'
        b"include_back_to_top = false\n"
        b"include_toc = false\n"
    )
    m = mocker.mock_open(read_data=mock_pyproject)
    mock_open = mocker.patch("pebbledoc.config.open", m)
    # ensure that the file "exists"
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.is_file", return_value=True)

    namespace = utils.prepare_namespace(
        package="test_package", config_file="pyproject.toml"
    )
    output = cli.build_config(namespace)
    assert_config(
        output,
        package="test_package",
        source_directory="~/pylibs/my_package",
        exclude=["my_func, MyClass"],
        admonition_style="classic",
        include_back_to_top=False,
        include_toc=False,
    )
    mock_open.assert_called_once_with(Path("pyproject.toml").resolve(), "rb")


def test_build_config_pebbledoc_config(mocker: MockerFixture) -> None:
    """Test building a config when defaults are in a pebbledoc.toml."""
    mock_pyproject = (
        b"[pebbledoc]\n"
        b'package_name = "test_package"\n'
        b'source_directory = "~/pylibs/my_package"\n'
        b'exclude = ["my_func, MyClass"]\n'
        b'admonition_style = "classic"\n'
        b"include_back_to_top = false\n"
        b"include_toc = false\n"
    )
    m = mocker.mock_open(read_data=mock_pyproject)
    mock_open = mocker.patch("pebbledoc.config.open", m)
    # ensure that the file "exists"
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.is_file", return_value=True)

    namespace = utils.prepare_namespace(
        package="test_package", config_file="pebbledoc.toml"
    )
    output = cli.build_config(namespace)
    assert_config(
        output,
        package="test_package",
        source_directory="~/pylibs/my_package",
        exclude=["my_func, MyClass"],
        admonition_style="classic",
        include_back_to_top=False,
        include_toc=False,
    )
    mock_open.assert_called_once_with(Path("pebbledoc.toml").resolve(), "rb")


def test_build_config_pyrpoject_cli_override(mocker: MockerFixture) -> None:
    """Test that CLI args override file configs."""
    mock_pyproject = (
        b"[tool.pebbledoc]\n"
        b'package_name = "test_package"\n'
        b'source_directory = "~/pylibs/my_package"\n'
        b'output = "MY_DOCS.md"\n'
        b'exclude = ["my_func, MyClass"]\n'
        b'admonition_style = "classic"\n'
        b"include_back_to_top = false\n"
        b"include_toc = false\n"
        b"collapsible_params = true\n"
    )
    m = mocker.mock_open(read_data=mock_pyproject)
    mock_open = mocker.patch("pebbledoc.config.open", m)
    # ensure that the file "exists"
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.is_file", return_value=True)

    namespace = utils.prepare_namespace(
        package="test_package",
        output="DOCUMENTATION.md",
        config_file="pyproject.toml",
        exclude=["MyClass"],  # only one of the two in the config file
        title="My custom title",
        admonition_style="map",
        no_module_docstring=True,
        no_collapsible_params=True,
    )
    output = cli.build_config(namespace)
    assert_config(
        output,
        package="test_package",
        source_directory="~/pylibs/my_package",
        output="DOCUMENTATION.md",
        exclude=["MyClass"],  # only the one from the CLI
        admonition_style="map",
        document_title="My custom title",
        include_back_to_top=False,
        include_toc=False,
        module_docstring=False,
        collapsible_params=False,
    )
    mock_open.assert_called_once_with(Path("pyproject.toml").resolve(), "rb")


def test_build_config_pebbledoc_cli_override(mocker: MockerFixture) -> None:
    """Test that CLI args override file configs."""
    mock_pyproject = (
        b"[pebbledoc]\n"
        b'package_name = "test_package"\n'
        b'source_directory = "~/pylibs/my_package"\n'
        b'output = "MY_DOCS.md"\n'
        b'exclude = ["my_func, MyClass"]\n'
        b'admonition_style = "classic"\n'
        b"include_back_to_top = false\n"
        b"include_toc = false\n"
    )
    m = mocker.mock_open(read_data=mock_pyproject)
    mock_open = mocker.patch("pebbledoc.config.open", m)
    # ensure that the file "exists"
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.is_file", return_value=True)

    namespace = utils.prepare_namespace(
        package="test_package",
        source_directory="~/external/projects/my_package",
        config_file="pebbledoc.toml",
        exclude=["my_decorator"],
        title="My custom title",
        admonition_style="map",
        no_module_docstring=True,
        no_collapsible_params=True,
    )
    output = cli.build_config(namespace)
    assert_config(
        output,
        package="test_package",
        source_directory="~/external/projects/my_package",
        output="MY_DOCS.md",
        exclude=["my_decorator"],
        admonition_style="map",
        document_title="My custom title",
        include_back_to_top=False,
        include_toc=False,
        module_docstring=False,
        collapsible_params=False,
    )
    mock_open.assert_called_once_with(Path("pebbledoc.toml").resolve(), "rb")


def test_build_config_missing_file(mocker: MockerFixture) -> None:
    """Test building a config when the given config file does not exist."""
    mock_open = mocker.patch("pebbledoc.config.open")
    # ensure that the file "does not exist"
    mocker.patch("pathlib.Path.exists", return_value=False)
    mocker.patch("pathlib.Path.is_file", return_value=True)

    namespace = utils.prepare_namespace(
        package="test_package", config_file="pyproject.toml"
    )
    with pytest.raises(FileNotFoundError) as exc_info:
        cli.build_config(namespace)
    path = Path("pyproject.toml").resolve()
    assert exc_info.value.args[0] == f"{path} is not a file or does not exist"
    mock_open.assert_not_called()


def test_build_config_only_directory(mocker: MockerFixture) -> None:
    """Test building a config when the given config file is a dir."""
    mock_open = mocker.patch("pebbledoc.config.open")
    # ensure that the file "does not exist"
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.is_file", return_value=False)

    namespace = utils.prepare_namespace(
        package="test_package", config_file="./src/"
    )
    with pytest.raises(FileNotFoundError) as exc_info:
        cli.build_config(namespace)
    path = Path("./src/").resolve()
    assert exc_info.value.args[0] == f"{path} is not a file or does not exist"
    mock_open.assert_not_called()


def test_build_config_invalid_file_name(mocker: MockerFixture) -> None:
    """Test building a config when the given config file name is invalid."""
    mock_open = mocker.patch("pebbledoc.config.open")
    # ensure that the file "does not exist"
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.is_file", return_value=True)

    namespace = utils.prepare_namespace(
        package="test_package", config_file="setup.cfg"
    )
    with pytest.raises(IOError) as exc_info:
        cli.build_config(namespace)
    assert exc_info.value.args[0] == (
        "Config file must be one of the following: pebbledoc.toml, "
        ".pebbledoc.toml, pyproject.toml"
    )
    mock_open.assert_not_called()


def test_build_config_unsupported_fields(mocker: MockerFixture) -> None:
    """Test that unsupported fields raise warnings."""
    mock_pyproject = (
        b"[pebbledoc]\n"
        b'package_name = "test_package"\n'
        b'admonition_style = "classic"\n'
        b'reference_color = "blue"\n'
        b"include_back_to_top = false\n"
        b"include_toc = false\n"
        b"imaginary_option = false\n"
    )
    m = mocker.mock_open(read_data=mock_pyproject)
    mock_open = mocker.patch("pebbledoc.config.open", m)
    # ensure that the file "exists"
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.is_file", return_value=True)

    namespace = utils.prepare_namespace(
        package="test_package", config_file="pebbledoc.toml"
    )
    with pytest.warns(UserWarning) as w_info:
        output = cli.build_config(namespace)
    assert_config(
        output,
        package="test_package",
        admonition_style="classic",
        include_back_to_top=False,
        include_toc=False,
    )
    assert str(w_info[0].message) == (
        "Config parameter 'reference_color' does not exist in pebbledoc"
    )
    assert str(w_info[1].message) == (
        "Config parameter 'imaginary_option' does not exist in pebbledoc"
    )
    assert not hasattr(output, "reference_color")
    assert not hasattr(output, "imaginary_option")
    mock_open.assert_called_once_with(Path("pebbledoc.toml").resolve(), "rb")


def test_build_config_file_discovery(mocker: MockerFixture) -> None:
    """Test discovering a config file when none is specified."""
    # we patch every interaction with the file system:
    mock_cwd = (
        "/home/user/pebbledoc/Documents/Python/stellarium_lite/src/"
        "stellarium_lite/observation"
    )
    mocker.patch("os.getcwd", return_value=mock_cwd)
    mock_cfg_file = Path(
        "/home/user/pebbledoc/Documents/Python/stellarium_lite/pebbledoc.toml"
    ).resolve()
    real_pathexists = Path.exists

    # we must patch Path.exists like this to not break pytest itself
    def patched_exists(self: Path) -> bool:
        if self.resolve() == mock_cfg_file:
            return True
        return real_pathexists(self)

    mocker.patch.object(
        Path, "exists", autospec=True, side_effect=patched_exists
    )
    mocker.patch("pathlib.Path.is_file", return_value=True)

    # patch opening of mock file
    mock_pyproject = (
        b"[pebbledoc]\n"
        b'package_name = "test_package"\n'
        b'admonition_style = "classic"\n'
        b"include_back_to_top = false\n"
        b"include_toc = false\n"
    )
    m = mocker.mock_open(read_data=mock_pyproject)
    mock_open = mocker.patch("pebbledoc.config.open", m)

    namespace = utils.prepare_namespace(package="test_package")
    output = cli.build_config(namespace)
    assert_config(
        output,
        package="test_package",
        admonition_style="classic",
        include_back_to_top=False,
        include_toc=False,
    )
    mock_open.assert_called_once_with(mock_cfg_file, "rb")
