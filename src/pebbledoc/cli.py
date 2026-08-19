"""Command line interface for pebbledoc."""

import argparse
import importlib.metadata
import sys
from pathlib import Path
from typing import Never

from . import documenting
from .config import build_config


def _build_parser() -> argparse.ArgumentParser:
    """
    Build argument parser for pebbledoc.

    :return: Argument parser for pebbledoc CLI.
    """
    description = (
        "pebbledoc is a lightweight documentation tool - automatically "
        "generate a single-file API documentation for your Python project!\n\n"
        "Note that the package you wish to document must either be installed "
        "in the same environment as pebbledoc, or you must specify its source "
        "directory when using pebbledoc. Either way, all of its dependencies "
        "must be installed."
    )
    parser = argparse.ArgumentParser(
        prog="pebbledoc",
        description=description,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"pebbledoc version {importlib.metadata.version('pebbledoc')}",
    )
    parser.add_argument(
        "-p",
        "--package",
        help="name of the package to document",
        metavar="",
        required=True,
    )
    parser.add_argument(
        "-s",
        "--source-directory",
        help=(
            "source directory of the package; must be specified if the "
            "package is not installed in the current environment"
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
        help="file containing pebbledoc configuration instructions, optional",
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
        help="omit module-level docstrings for submodules and sub-packages",
        action="store_true",
    )
    options.add_argument(
        "--no-include-constants",
        help="omit constants defined as module-level globals",
        action="store_true",
    )
    options.add_argument(
        "--no-toc",
        help="omit the table of contents at the beginning of the file",
        action="store_true",
    )
    options.add_argument(
        "--no-back-to-top",
        help="omit the 'back to top' links at the beginning of each section",
        action="store_true",
    )
    options.add_argument(
        "--no-main-module-header",
        help="omit the h2 header for the main module",
        action="store_true",
    )

    return parser


def _error(msg: str) -> None:
    """Helper function to emit to ``stderr``."""
    print(f"\033[91mError:\033[0m {msg}", file=sys.stderr)


def _handle_args(args: argparse.Namespace) -> int:
    """
    Handle the given configuration and run pebbledoc.

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
        _error(f"Could not locate config file: {exc_info}")
        return 4

    output = Path(config.output).resolve()
    if output.exists() and output.is_dir():
        _error("Output must be a file, not a directory")
        return 1
    elif not output.parent.exists():
        _error(f"Output directory {output.parent} does not exist")
        return 1

    source_dir = config.source_directory
    if isinstance(source_dir, str):
        source_dir = Path(args.source_directory).resolve()
    if source_dir is not None and not source_dir.exists():
        _error(f"Source directory {source_dir} does not exist")
        return 1
    if source_dir is not None:
        sys.path.insert(0, str(source_dir))

    try:
        document_str = documenting.markdown_documentation(args.package, config)
    except ImportError as exc_info:
        _error(
            f"Could not import package {args.package} or its dependencies: {exc_info}"
        )
        return 2
    except FileNotFoundError as exc_info:
        _error(f"One or more (sub-)packages could not be found: {exc_info}")
        return 5
    finally:
        if source_dir is not None:
            sys.path.remove(str(source_dir))

    try:
        with open(output, "w") as f:
            f.write(document_str)
    except IOError as exc_info:
        _error(f"Could not write {output}: {exc_info}")
        return 3

    return 0


def main() -> Never:
    parser = _build_parser()
    args = parser.parse_args()
    sys.exit(_handle_args(args))
