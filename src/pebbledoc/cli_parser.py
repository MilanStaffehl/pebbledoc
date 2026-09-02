"""Parser and parser utilities for the command line interface."""

import argparse
import importlib.metadata
import textwrap


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

    source_group = parser.add_argument_group(title="source")
    source_group.add_argument(
        "-p",
        "--package",
        help="name of the package to document",
        metavar="",
        required=True,
    )
    source_group.add_argument(
        "-s",
        "--source-directory",
        help=(
            "source directory of the package; must be specified if the "
            "package is not installed in the current environment"
        ),
        metavar="",
        default=None,
    )
    source_group.add_argument(
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
    source_group.add_argument(
        "--config-file",
        help="file containing pebbledoc configuration instructions, optional",
        metavar="",
        default=None,
    )

    output_group = parser.add_argument_group(title="output")
    output_group.add_argument(
        "-o",
        "--output",
        help="name and filepath of the output file",
        metavar="",
        default=None,
    )
    output_group.add_argument(
        "--diff",
        help=(
            "show changes with respect to existing file instead of writing "
            "docs to file"
        ),
        action="store_true",
    )
    output_group.add_argument(
        "--exit-code",
        help="exit with non-zero exit code when documentation changes",
        action="store_true",
    )

    rendering_group = parser.add_argument_group(title="rendering")
    rendering_group.add_argument(
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
    rendering_group.add_argument(
        "--title",
        help="set the title for the document (i.e. its main header)",
        metavar="",
        default=None,
    )

    formatting_group = parser.add_argument_group(title="formatting")
    formatting_group.add_argument(
        "--no-generic-intro",
        help="omit the generic introduction after the main header",
        action="store_true",
    )
    formatting_group.add_argument(
        "--no-module-docstring",
        help="omit module-level docstrings for submodules and sub-packages",
        action="store_true",
    )
    formatting_group.add_argument(
        "--no-include-constants",
        help="omit constants defined as module-level globals",
        action="store_true",
    )
    formatting_group.add_argument(
        "--no-toc",
        help="omit the table of contents at the beginning of the file",
        action="store_true",
    )
    formatting_group.add_argument(
        "--no-back-to-top",
        help="omit the 'back to top' links at the beginning of each section",
        action="store_true",
    )
    formatting_group.add_argument(
        "--no-main-module-header",
        help="omit the h2 header for the main module",
        action="store_true",
    )
    formatting_group.add_argument(
        "--no-collapsible-params",
        help=(
            "render parameter info field lists as static lists instead of "
            "collapsible sections"
        ),
        action="store_true",
    )
    formatting_group.add_argument(
        "--no-references",
        help="do not turn Sphinx-style references into hyperlinks",
        action="store_true",
    )
    formatting_group.add_argument(
        "--no-full-toc-name",
        help="use only shortened member names in table of contents",
        action="store_true",
    )
    formatting_group.add_argument(
        "--no-preserve-linewraps",
        help="remove stylistic line wraps (singular line breaks) in texts",
        action="store_true",
    )

    return parser
