"""Command line interface for pebbledoc."""

import argparse
import difflib
import importlib.metadata
import sys
import textwrap
from collections.abc import Iterator
from pathlib import Path
from typing import Never

import colorama

from . import documenting
from .config import build_config


class PebbledocHelpTextFormatter(argparse.HelpFormatter):
    """
    Custom help text formatter for pebbledoc.

    The formatter preserves formatting in the description and the
    argument help texts, but without wrapping in the middle of words.
    Help texts are also correctly indented when wrapped. The formatter
    also correctly identifies lists starting with ``-`` or ``*`` as
    bullets, and correctly indents any list items that need to be
    wrapped.
    """

    def __init__(
        self,
        prog: str,
        indent_increment: int = 2,
        max_help_position: int = 28,
        width: int | None = None,
    ) -> None:
        """Set custom max. help text position."""
        super().__init__(prog, indent_increment, max_help_position, width)

    def _fill_text(self, text: str, width: int, indent: str) -> str:
        wrapped = []
        for line in text.split("\n"):
            if line:
                wrapped += textwrap.wrap(
                    line,
                    width,
                    initial_indent=indent,
                    subsequent_indent=indent,
                )
            else:
                wrapped.append(line)
        return "\n".join(wrapped)

    def _split_lines(self, text: str, width: int) -> list[str]:
        lines = text.splitlines()
        wrapped = []
        for line in lines:
            if line.startswith("- ") or line.startswith("* "):
                indent = "  "
            else:
                indent = ""
            wrapped += textwrap.wrap(line, width, subsequent_indent=indent)
        return wrapped


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
        formatter_class=PebbledocHelpTextFormatter,
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
        "-x",
        "--exclude",
        help=(
            "names of members to exclude from the documentation, separated "
            "by whitespace"
        ),
        metavar="member",
        nargs="+",
        default=None,
    )
    parser.add_argument(
        "-a",
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
        "-t",
        "--title",
        help="set the title for the document (i.e. its main header)",
        metavar="",
        default=None,
    )
    parser.add_argument(
        "--diff",
        help=(
            "show changes with respect to existing file instead of writing "
            "docs to file"
        ),
        action="store_true",
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
    options.add_argument(
        "--no-collapsible-params",
        help=(
            "render parameter info field lists as static lists instead of "
            "collapsible sections"
        ),
        action="store_true",
    )
    options.add_argument(
        "--no-references",
        help="do not turn Sphinx-style references into hyperlinks",
        action="store_true",
    )
    options.add_argument(
        "--no-full-toc-name",
        help="use only shortened member names in table of contents",
        action="store_true",
    )
    options.add_argument(
        "--no-preserve-linewraps",
        help="remove stylistic line wraps (singular line breaks) in texts",
        action="store_true",
    )

    return parser


def _error(msg: str) -> None:
    """Helper function to emit to ``stderr``."""
    red = colorama.Fore.RED
    reset = colorama.Style.RESET_ALL
    print(f"{red}Error:{reset} {msg}", file=sys.stderr)


def _diff(diff: Iterator[str]) -> None:
    """Helper function to color and emit unified diffs."""
    for line in diff:
        if line.startswith("+"):
            start = colorama.Fore.GREEN
            end = colorama.Style.RESET_ALL
        elif line.startswith("-"):
            start = colorama.Fore.RED
            end = colorama.Style.RESET_ALL
        elif line.startswith("@@"):
            start = colorama.Fore.BLUE
            end = colorama.Style.RESET_ALL
        else:
            start = ""
            end = ""
        print(f"{start}{line.removesuffix('\n')}{end}")


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
    # attempt to find the configuration file
    try:
        config = build_config(args)
    except IOError as exc_info:
        _error(f"Could not locate config file: {exc_info}")
        return 4

    # check that the given output is valid
    output = Path(config.output).resolve()
    if output.exists() and output.is_dir():
        _error("Output must be a file, not a directory")
        return 1
    elif not output.parent.exists():
        _error(f"Output directory {output.parent} does not exist")
        return 1

    # add source directory to PATH, if provided
    source_dir = config.source_directory
    if isinstance(source_dir, str):
        source_dir = Path(args.source_directory).resolve()
    if source_dir is not None and not source_dir.exists():
        _error(f"Source directory {source_dir} does not exist")
        return 1
    if source_dir is not None:
        sys.path.insert(0, str(source_dir))

    # generate documentation
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

    # check if the file would change
    if output.exists():
        with open(output, "r") as stream:
            old_content = stream.read()
        old_file = output.name
    else:
        old_content = ""
        old_file = "<none>"
    # ignore newlines at end of file (might be added/removed by linters)
    old_content = old_content.rstrip("\n")
    new_content = document_str.rstrip("\n")

    # print diff, if requested
    if args.diff:
        diff = difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=old_file,
            tofile=str(output.name),
        )
        _diff(diff)
        return 0

    # if no changes (except newlines at the end) occur, exit now
    if old_content == new_content:
        return 0

    # otherwise, create documentation file
    try:
        with open(output, "w") as f:
            f.write(document_str)
    except IOError as exc_info:
        _error(f"Could not write {output}: {exc_info}")
        return 3

    return 0


def main() -> Never:
    """Entry point for pebbledoc as a command-line tool."""
    colorama.just_fix_windows_console()
    parser = _build_parser()
    args = parser.parse_args()
    sys.exit(_handle_args(args))
