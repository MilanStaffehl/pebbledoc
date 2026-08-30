"""Command line interface for pebbledoc."""

import argparse
import contextlib
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
    parser.add_argument(
        "--exit-code",
        help="Exit with non-zero exit code when documentation changes",
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


def _validate_source_directory(source_directory: str | None) -> Path | None:
    """
    Validate the user-supplied source directory.

    Function checks that the directory exists, and is indeed a directory.
    If any check fails, a ValueError is raised.

    :param source_directory: The user-supplied source directory as string,
        or None if the user supplied no source directory.
    :raises ValueError: If the supplied source directory does not exist
        or is not a directory.
    :return: The supplied source directory as a Path object or, if the
        user specified no source directory, None.
    """
    if isinstance(source_directory, str):
        source_dir = Path(source_directory).resolve()
    else:
        source_dir = source_directory
    if source_dir is not None and not source_dir.exists():
        raise ValueError(f"Source directory {source_dir} does not exist")
    return source_dir


def _validate_output_path(output_path: str) -> Path:
    """
    Validate the user-supplied output path.

    The function checks that the supplied path points to a file, not a
    directory, and that all parent directories exist. If any check fails,
    the function raises a ValueError. The function finally returns a
    resolved path to the output file.

    :param output_path: User-supplied output path as string.
    :raises ValueError: If any check of the requirements on the path
        fail.
    :return: The resolved path to the output file.
    """
    output = Path(output_path).resolve()
    if output.exists() and output.is_dir():
        raise ValueError("Output must be a file, not a directory")
    elif not output.parent.exists():
        raise ValueError(f"Output directory {output.parent} does not exist")
    return output


@contextlib.contextmanager
def _source_path_inserted_to_path(source_path: Path | None) -> Iterator[None]:
    """
    Insert the given source path into PATH within the context.

    The context manager adds the provided source path into the PATH and
    removes it again once the context manager exits. Any exceptions are
    propagated upwards, but the source directory will still be removed
    from the PATH. If the source path is None, the context manager does
    nothing.

    :param source_path:
    :return:
    """
    if source_path is None:
        yield
        return
    sys.path.insert(0, str(source_path))
    try:
        yield
    finally:
        sys.path.remove(str(source_path))


def _read_existing_docs(output: Path) -> tuple[str, str]:
    """
    Find and read an already existing docs file from a previous run.

    Function returns a tuple of strings, with the first being the text
    of the already existing file, and the second being its name. If no
    file exists yet, the first string is empty, and the second one is
    ``<none>`` to indicate that there was no previous file. These values
    can be used for creation of a diff.

    :param output: The path to the documentation file that will be
        created and which might already exist from a previous run.
    :return: Tuple of strings, with the first being the text of the old
        file, and the second being the name of the new file.
    """
    if output.exists():
        with open(output, "r") as stream:
            old_content = stream.read()
        old_file = output.name
    else:
        old_content = ""
        old_file = "<none>"
    return old_content, old_file


def _regular_exit(docs_unchanged: bool, emit_exit_code: bool) -> int:
    """
    Return exit code according to flag ``--exit-code`` being set or not.

    :param docs_unchanged: Whether the document actually changed.
    :param emit_exit_code: Whether to emit a non-zero exit code if the
        docs changed.
    :return: Zero if docs didn't change or no non-zero exit code was
        requested for changed files. If a non-zero exit code was
        requested and the files did change, returns the exit code
        dedicated to indicate changed file contents.
    """
    if emit_exit_code and not docs_unchanged:
        return 255
    return 0


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

    # check that the given output and source dir are valid
    try:
        output = _validate_output_path(config.output)
        source_dir = _validate_source_directory(config.source_directory)
    except ValueError as exc_info:
        _error(str(exc_info))
        return 1

    # generate documentation
    try:
        with _source_path_inserted_to_path(source_dir):
            document_str = documenting.markdown_documentation(
                args.package, config
            )
    except ImportError as exc_info:
        _error(
            f"Could not import package {args.package} or its dependencies: {exc_info}"
        )
        return 2
    except FileNotFoundError as exc_info:
        _error(f"One or more (sub-)packages could not be found: {exc_info}")
        return 5

    # check if the file would change
    old_content, old_file = _read_existing_docs(output)
    # ignore newlines at end of file (might be added/removed by linters)
    old_content = old_content.rstrip("\n")
    new_content = document_str.rstrip("\n")
    docs_unchanged = old_content == new_content

    # if no changes (except newlines at the end) occur, exit now
    if docs_unchanged:
        return 0

    # print diff, if requested
    if args.diff:
        diff = difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=old_file,
            tofile=str(output.name),
        )
        _diff(diff)
        return _regular_exit(docs_unchanged, args.exit_code)

    # otherwise, create documentation file
    try:
        with open(output, "w") as f:
            f.write(document_str)
    except IOError as exc_info:
        _error(f"Could not write {output}: {exc_info}")
        return 3

    # exit with non-zero exit code if docs changed and instructed to do so:
    return _regular_exit(docs_unchanged, args.exit_code)


def main() -> Never:
    """Entry point for pebbledoc as a command-line tool."""
    colorama.just_fix_windows_console()
    parser = _build_parser()
    args = parser.parse_args()
    sys.exit(_handle_args(args))
