"""Utilities for testing."""

import argparse


def prepare_namespace(
    *,
    package: str = "stellarium_lite",
    source_directory: str | None = None,
    output: str | None = None,
    config_file: str | None = None,
    admonition_style: str | None = None,
    title: str | None = None,
    no_module_docstring: bool = False,
    no_include_constants: bool = False,
    no_toc: bool = False,
    no_back_to_top: bool = False,
) -> argparse.Namespace:
    """
    Create a namespace with the attributes that minidoc expects.

    This function basically takes over the role of the user giving the
    application command line arguments. It takes all arguments and passes
    them on to a blank namespace object as-is, which is then returned.
    The parameter defaults are identical to that of the CLI.
    """
    return argparse.Namespace(**locals())
