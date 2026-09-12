"""Command line interface logic for pebbledoc."""

import argparse
import contextlib
import difflib
import enum
import re
import sys
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Never

import colorama

from . import documenting
from .cli_parser import _build_parser
from .config import PebbledocConfig, build_config

type DocsHandlerFunc = Callable[
    [Path, Path | None, PebbledocConfig], tuple[str, str, str]
]


class _ErrorCodes(enum.IntEnum):
    """Error codes for pebbledoc."""

    EX_SUCCESS = 0
    """Execution was successful."""

    EX_GENERIC_ERROR = 1
    """A generic, unspecified error occurred."""

    EX_BAD_ARGS = 2
    """Invalid arguments were given (automatically used by argparse)."""

    EX_IMPORT_ERR = 3
    """The package to document could not be imported."""

    EX_INVALID_PATH = 4
    """A user-supplied path is invalid."""

    EX_CANT_WRITE = 5
    """The output file could not be written."""

    EX_MISSING_CONFIG = 6
    """The user-specified config file was not found."""

    EX_NO_ORIGIN = 7
    """The origin of a (sub-)package could not be found."""

    EX_INVALID_TARGET_HEADER = 8
    """The target header does not exist in the targeted file."""

    EX_DOCS_CHANGED = 255
    """Emitted when docs change and non-zero exit was requested by user."""


class _PebbledocError(Exception):
    """
    Raised when pebbledoc encounters an exception during execution.

    In addition to an exception message, the exception also holds the
    exit code with which pebbledoc should exit when handling the event
    that led to this exception.
    """

    def __init__(self, exit_code: _ErrorCodes, *args: object):
        self.exit_code = exit_code
        super().__init__(*args)

    def __str__(self) -> str:
        """Append cause to the message, if present."""
        previous = self.__cause__
        msg = super().__str__()
        if previous:
            msg += f": {str(previous)}"
        return msg


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
        raise _PebbledocError(
            _ErrorCodes.EX_INVALID_PATH,
            f"Source directory {source_dir} does not exist",
        )
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
        raise _PebbledocError(
            _ErrorCodes.EX_INVALID_PATH,
            "Output must be a file, not a directory",
        )
    elif not output.parent.exists():
        raise _PebbledocError(
            _ErrorCodes.EX_INVALID_PATH,
            f"Output directory {output.parent} does not exist",
        )
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


def _read_existing_docs(output: Path) -> str:
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
    else:
        old_content = ""
    return old_content


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
        return _ErrorCodes.EX_DOCS_CHANGED
    return _ErrorCodes.EX_SUCCESS


def _handler_default(
    output: Path,
    source_dir: Path | None,
    config: PebbledocConfig,
) -> tuple[str, str, str]:
    """
    Handler for generating standalone documentation files.

    This function handles generating a standalone documentation file for
    the package and configuration provided. For standalone files, the
    entire file content is managed by ``pebbledoc``, so this function
    returns the whole file content for both the documentation string and
    the final file content. Similarly, if a previous version of the doc
    exists on file, this handler returns the whole content.

    :param output: The path to the documentation file that will be
        created and which might already exist from a previous run.
    :param source_dir: The path to the source directory from where to
        import the package, if it isn't already installed. Can be None
        to signal that the package is already installed.
    :param config: The configuration object, constructed from CLI args
        and potentially discovered or provided config files.
    :return: A tuple of three strings:

        1. The content of the old documentation file (all of it), if an
           older version exists. Otherwise, this will be an empty string.
        2. The content of the newly generated documentation file (the
           full file content), will be used in the diff check.
        3. Same as 2; this is the content that will be written into the
           file at the end.
    """
    try:
        with _source_path_inserted_to_path(source_dir):
            document_str = documenting.markdown_documentation(
                config.package_name, config
            )
    except ImportError as prev_exc:
        fatal_exc = _PebbledocError(
            _ErrorCodes.EX_IMPORT_ERR,
            f"Could not import package {config.package_name} or its "
            f"dependencies",
        )
        raise fatal_exc from prev_exc
    except FileNotFoundError as prev_exc:
        fatal_exc = _PebbledocError(
            _ErrorCodes.EX_NO_ORIGIN,
            "One or more (sub-)packages could not be found",
        )
        raise fatal_exc from prev_exc

    # check if the file would change
    old_content = _read_existing_docs(output)

    return old_content, document_str, document_str


def _handler_targeted_header(
    output: Path,
    source_dir: Path | None,
    config: PebbledocConfig,
) -> tuple[str, str, str]:
    """
    Handler for inserting documentation under headers in output file.

    This function handles inserting the documentation generated for the
    package and configuration provided into the existing output file
    under the specified target header. For targeted files, only the
    targeted section is managed by ``pebbledoc``, so this function
    returns only the old and new documentation section for the diff
    check. However, the third return value is the entire new file, which
    includes preceding and following sections as well.

    If there is no existing output file or that file does not contain
    the correct header, the function raises a ``_PebbledocError``
    exception, which will cause ``pebbledoc`` to terminate.

    :param output: The path to the documentation file that will be
        created and which might already exist from a previous run.
    :param source_dir: The path to the source directory from where to
        import the package, if it isn't already installed. Can be None
        to signal that the package is already installed.
    :param config: The configuration object, constructed from CLI args
        and potentially discovered or provided config files.
    :return: A tuple of three strings:

        1. The content of the old documentation section (only what is
           found under the targeted header. Will be used in diff check.
        2. The content of the newly generated documentation section (as
           it will be inserted), which will be used in the diff check.
        3. The full content of the updated target file, with the new
           documentation inserted into the targeted section. Will be
           written to file, but will not be used in diff check.
    """
    # tell type checkers we are sure the header is not None
    assert config.target_header is not None

    # output file must already exist
    if not output.exists():
        raise _PebbledocError(
            _ErrorCodes.EX_INVALID_PATH,
            f"Targeted file {output} does not exist, can't insert documentation",
        )

    # get targeted file
    old_content = _read_existing_docs(output)

    # find the targeted header and check its level
    header_pattern = re.compile(
        r"^(#{1,6})[ \t]+" + re.escape(config.target_header) + r"[ \t]*$",
        re.MULTILINE,
    )
    header_match = re.search(header_pattern, old_content)
    if not header_match:
        raise _PebbledocError(
            _ErrorCodes.EX_INVALID_TARGET_HEADER,
            f"The output file does not contain the target header "
            f"'{config.target_header}'",
        )
    header_level = len(header_match.group(1))

    # find the previous content
    start = header_match.end()
    next_header_pattern = re.compile(
        r"^#{1," + str(header_level) + r"}[ \t]+.+$",
        re.MULTILINE,
    )
    next_header_match = next_header_pattern.search(old_content, pos=start)
    if not next_header_match:
        end = len(old_content)
    else:
        end = next_header_match.start()
    old_docs = old_content[start:end].lstrip("\n")

    # generate the new documentation
    additional_header_level = header_level - 1
    try:
        with _source_path_inserted_to_path(source_dir):
            new_docs = documenting.markdown_documentation(
                config.package_name, config, additional_header_level
            )
    except ImportError as prev_exc:
        fatal_exc = _PebbledocError(
            _ErrorCodes.EX_IMPORT_ERR,
            f"Could not import package {config.package_name} or its "
            f"dependencies",
        )
        raise fatal_exc from prev_exc
    except FileNotFoundError as prev_exc:
        fatal_exc = _PebbledocError(
            _ErrorCodes.EX_NO_ORIGIN,
            "One or more (sub-)packages could not be found",
        )
        raise fatal_exc from prev_exc

    # build new document
    head = old_content[:start].rstrip("\n")
    tail = old_content[end:].rstrip("\n")
    margin = "\n\n" if end != len(old_content) else ""
    new_content = f"{head}\n\n{new_docs.rstrip('\n')}\n\n{tail}{margin}"
    return old_docs, new_docs, new_content


def _handle_args(args: argparse.Namespace) -> int:
    """
    Handle the given configuration and run pebbledoc.

    Function returns an error code when something goes wrong. The error
    codes have the following meaning:

    - 1: A generic, unspecified error occurred.
    - 3: The package to document or its dependencies could not be
      imported.
    - 4: Either the given source or output paths are invalid.
    - 5: The output file could not be written.
    - 6: The specified config file could not be located.
    - 7: The package or one of its subpackages did not provide a list
      of members for its API (i.e. it had no ``__all__``), and an
      attempt at finding its public members using AST parsing failed due
      to the origin of the package not being discoverable.
    - 255: Execution was successful, but the ``--exit-code`` flag was
      set and requested a non-zero exit code when the documentation
      changed from its previous state.

    :param args: The ``argparse.Namespace`` object created from the user
        input.
    :return: An exit code, which is handed to ``sys.exit``.
    """
    # attempt to find the configuration file
    try:
        config = build_config(args)
    except IOError as exc_info:
        _error(f"Could not locate config file: {exc_info}")
        return _ErrorCodes.EX_MISSING_CONFIG

    # check that a package name was provided
    if not config.package_name:
        _error(
            "No package to document was specified - use the `--package` "
            "option to specify a package"
        )
        return _ErrorCodes.EX_BAD_ARGS  # equivalent to a missing argument

    # check that the given output and source dir are valid
    try:
        output = _validate_output_path(config.output)
        source_dir = _validate_source_directory(config.source_directory)
    except _PebbledocError as exc_info:
        _error(str(exc_info))
        return exc_info.exit_code

    # get the new and old documentation, and the new file content
    handler: DocsHandlerFunc
    if config.target_header is not None:
        handler = _handler_targeted_header
    else:
        handler = _handler_default
    try:
        old_docs, new_docs, document_str = handler(output, source_dir, config)
    except _PebbledocError as exc_info:
        _error(str(exc_info))
        return exc_info.exit_code

    # check if the documentation has changed; ignore newlines at end of
    # file (might be added/removed by linters)
    old_docs = old_docs.rstrip("\n")
    new_docs_ = new_docs.rstrip("\n")  # do not alter actual string
    docs_unchanged = old_docs == new_docs_

    # if no changes (except newlines at the end) occur, exit now
    if docs_unchanged:
        return _ErrorCodes.EX_SUCCESS

    # print diff, if requested
    if args.diff:
        old_file = output.name if output.exists() else "<none>"
        diff = difflib.unified_diff(
            old_docs.splitlines(keepends=True),
            new_docs_.splitlines(keepends=True),
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
        return _ErrorCodes.EX_CANT_WRITE

    # exit with non-zero exit code if docs changed and instructed to do so:
    return _regular_exit(docs_unchanged, args.exit_code)


def main() -> Never:
    """Entry point for pebbledoc as a command-line tool."""
    try:
        colorama.just_fix_windows_console()
        parser = _build_parser()
        args = parser.parse_args()
        sys.exit(_handle_args(args))
    except Exception as exc_info:
        _error(f"Encountered an unexpected error: {exc_info}")
        sys.exit(_ErrorCodes.EX_GENERIC_ERROR)
