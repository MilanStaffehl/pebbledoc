"""Command line interface for Minidoc MD."""

import argparse
import importlib.metadata
import sys
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
    )
    parser.add_argument(
        "-o",
        "--output",
        help="name and filepath of the output file",
        metavar="",
        default="API.md",
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
        default="mix",
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

    return parser


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
    config = MinidocConfig(
        admonition_strategy=args.admonition_style,
        document_constants=not args.no_include_constants,
        module_docstring=not args.no_module_docstring,
        include_toc=not args.no_toc,
    )

    output = Path(args.output)
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
