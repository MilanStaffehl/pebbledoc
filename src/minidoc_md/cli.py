"""Command line interface for Minidoc MD."""

import argparse
import importlib.metadata
import os
import sys
import tomllib
import warnings
from pathlib import Path
from typing import Final, Never

from minidoc_md import minidoc
from minidoc_md.config import MinidocConfig

# CAUTION: Order of the list determines order of precedence!
# pyproject.toml is last, so that an existing pyproject.toml with no
# minidoc-md config values does not overrule any other config file.
SUPPORTED_CONFIG_FILES: Final[list[str]] = [
    "minidoc-md.toml",
    ".minidoc-md.toml",
    "pyproject.toml",
]


def _build_parser() -> argparse.ArgumentParser:
    """
    Build argument parser for Minidoc MD.

    :return: Argument parser for minidoc-md CLI.
    """
    description = (
        "minidoc-md is a lightweight documentation tool - automatically "
        "generate a single-file API documentation for your Python project!\n\n"
        "Note that the package you wish to document must either be installed "
        "in the same environment as minidoc-md, or you must specify its source "
        "directory when using minidoc-md. Either way, all of its dependencies "
        "must be installed."
    )
    parser = argparse.ArgumentParser(
        prog="minidoc-md",
        description=description,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"minidoc-md version {importlib.metadata.version('minidoc-md')}",
    )
    parser.add_argument(
        "-p",
        "--package",
        help="name of the package to document.",
        metavar="",
        required=True,
    )
    parser.add_argument(
        "-s",
        "--source-directory",
        help=(
            "source directory of the package, must be specified if the "
            "package is not installed in the current environment."
        ),
        metavar="",
        default=None,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="name and filepath of the output file",
        metavar="",
        default=None,
    )
    parser.add_argument(
        "-c",
        "--config-file",
        help="file containing minidoc-md configuration instructions, optional",
        metavar="",
        default=None,
    )
    parser.add_argument(
        "--admonition-style",
        help=(
            "rendering style for admonitions:\n"
            "- classic: render all admonitions as block quotes with headers "
            "in bold type\n"
            "- mix: render admonitions supported by GitHub in GitHub style, "
            "all others in classic style\n"
            "- github: render all admonitions in GitHub style, as block "
            "quotes with headers of the form [!TYPE]\n"
            "- map: render all admonitions in GitHub style, map unsupported "
            "admonitions to the closest supported type"
        ),
        choices=["classic", "mix", "github", "map"],
        default=None,
    )
    parser.add_argument(
        "--title",
        help="set the title for the document (i.e. its main header)",
        metavar="",
        default=None,
    )

    options = parser.add_argument_group(title="formatting")
    options.add_argument(
        "--no-module-docstring",
        help="omit module-level docstrings for submodules and sub-packages.",
        action="store_true",
    )
    options.add_argument(
        "--no-include-constants",
        help="omit constants defined as module-level globals.",
        action="store_true",
    )
    options.add_argument(
        "--no-toc",
        help="omit the table of contents at the beginning of the file.",
        action="store_true",
    )
    options.add_argument(
        "--no-back-to-top",
        help="omit the 'back to top' links at the beginning of each section.",
        action="store_true",
    )

    return parser


def _update_for_cli_args(
    config: MinidocConfig, args: argparse.Namespace
) -> MinidocConfig:
    """
    Update an existing config file for CLI arguments explicitly given.

    :param config: The existing config object to update.
    :param args: The argparse namespace object retrieved from the CLI.
    :return: The config, with all explicitly provided arguments replaced.
    """
    # overwrite with CLI arguments, if given:
    if args.admonition_style is not None:
        config.admonition_style = args.admonition_style
    if args.title is not None:
        config.document_title = args.title

    # and finally, overwrite options, if given
    options = {
        "no_module_docstring": "module_docstring",
        "no_include_constants": "document_constants",
        "no_toc": "include_toc",
        "no_back_to_top": "include_back_to_top",
    }
    for arg_name, config_name in options.items():
        if getattr(args, arg_name):
            setattr(config, config_name, False)

    return config


def _discover_config_file() -> Path | None:
    """
    Ascend from CWD upwards to find nearest config file.

    The function finds the nearest supported minidoc-md config file by
    ascending from the current working directory, and returns it, once
    it finds one. If no such file is found, it returns None.

    :return: Either the path to the nearest valid config file, or None.
    """
    current_dir = Path(os.getcwd())
    while True:
        for filename in SUPPORTED_CONFIG_FILES:
            config_file = current_dir / filename
            if config_file.exists():
                return config_file
        parent = current_dir.parent
        if parent == current_dir:
            break
        current_dir = parent
    return None


def build_config(args: argparse.Namespace) -> MinidocConfig:
    """
    Build a MinidocConfig from the command line arguments and config file.

    :param args: The namespace object retrieved from the CLI argparser.
    :return: A MinidocConfig object, built according to the CLI args.
    """
    # initialize the default config
    config = MinidocConfig(
        package_name=args.package,
        admonition_style="mix",
        document_title=None,
        document_constants=True,
        module_docstring=True,
        include_toc=True,
        include_back_to_top=True,
    )

    # check if there is a config
    config_file = args.config_file
    if config_file is None:
        config_file = _discover_config_file()
    if config_file is None:
        return _update_for_cli_args(config, args)

    # load the config
    config_path = Path(config_file).resolve()
    if not config_path.exists() or not config_path.is_file():
        raise FileNotFoundError(
            f"{config_path} is not a file or does not exist"
        )

    # get the config values as dictionary
    if config_path.name not in SUPPORTED_CONFIG_FILES:
        raise IOError(
            f"Config file must be one of the following: "
            f"{', '.join(SUPPORTED_CONFIG_FILES)}"
        )
    with open(config_path, "rb") as f:
        loaded_file = tomllib.load(f)
    if config_path.name == "pyproject.toml":
        base_config = loaded_file.get("tool", {}).get("minidoc", {})
    else:
        base_config = loaded_file["minidoc"]

    # set values if they are given
    for key, value in base_config.items():
        if not hasattr(config, key):
            warnings.warn(
                f"Config parameter '{key}' does not exist in minidoc-md",
                UserWarning,
                stacklevel=2,
            )
            continue
        setattr(config, key, value)
    return _update_for_cli_args(config, args)


def error(msg: str) -> None:
    """Helper function to emit to ``stderr``."""
    print(f"\033[91mError:\033[0m {msg}", file=sys.stderr)


def handle_args(args: argparse.Namespace) -> int:
    """
    Handle the given configuration and run minidoc-md.

    Function returns an error code when something goes wrong. The error
    codes have the following meaning:

    - 1: Either the given source or output paths are invalid.
    - 2: The package to document or its dependencies could not be
      imported.
    - 3: The output file could not be written.
    - 4: The specified config file could not be located.
    - 5: The package or one of its subpackages did not provide a list
      of members for its API (i.e. it had no ``__all__``), and an
      attempt at finding its public members using AST parsing failed due
      to the origin of the package not being discoverable.

    :param args: The ``argparse.Namespace`` object created from the user
        input.
    :return: An exit code, which is handed to ``sys.exit``.
    """
    try:
        config = build_config(args)
    except IOError as exc_info:
        error(f"Could not locate config file: {exc_info}")
        return 4

    output = Path(args.output) if args.output else Path("API.md")
    if output.exists() and output.is_dir():
        error("Output must be a file, not a directory")
        return 1
    elif not output.parent.exists():
        error(f"Output directory {output.parent} does not exist")
        return 1

    source_dir = args.source_directory
    if isinstance(source_dir, str):
        source_dir = Path(args.source_directory).resolve()
    if source_dir is not None and not source_dir.exists():
        error(f"Source directory {source_dir} does not exist")
        return 1
    if source_dir is not None:
        sys.path.insert(0, str(source_dir))

    try:
        package = importlib.import_module(args.package)
        document_str = minidoc.markdown_documentation(
            args.package, package, config
        )
    except ImportError as exc_info:
        error(
            f"Could not import package {args.package} or its dependencies: {exc_info}"
        )
        return 2
    except FileNotFoundError as exc_info:
        error(f"One or more (sub-)packages could not be found: {exc_info}")
        return 5
    finally:
        if source_dir is not None:
            sys.path.remove(str(source_dir))

    try:
        with open(output, "w") as f:
            f.write(document_str)
    except IOError as exc_info:
        error(f"Could not write {output}: {exc_info}")
        return 3

    return 0


def main() -> Never:
    parser = _build_parser()
    args = parser.parse_args()
    sys.exit(handle_args(args))
