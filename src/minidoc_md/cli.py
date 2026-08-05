"""Command line interface for Minidoc MD."""

import argparse
import importlib.metadata
import sys
import tomllib
import warnings
from pathlib import Path
from typing import Never

from minidoc_md import minidoc
from minidoc_md.config import MinidocConfig


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
        return _update_for_cli_args(config, args)

    # load the config
    config_path = Path(config_file).resolve()
    if not config_path.exists() or not config_path.is_file():
        raise FileNotFoundError(
            f"{config_path} is not a file or does not exist"
        )

    # get the config values as dictionary
    supported_formats = [
        "pyproject.toml",
        "minidoc-md.toml",
        ".minidoc-md.toml",
    ]
    if config_path.name not in supported_formats:
        raise IOError(
            f"Config file must either be one of the following: "
            f"{', '.join(supported_formats)}"
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
