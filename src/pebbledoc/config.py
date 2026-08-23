"""
Config object to hold various input options.
"""

import tomllib
import warnings
from argparse import Namespace
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

from .types import AdmonitionStyle

# CAUTION: Order of the list determines order of precedence!
# pyproject.toml is last, so that an existing pyproject.toml with no
# pebbledoc config values does not overrule any other config file.
SUPPORTED_CONFIG_FILES: Final[list[str]] = [
    "pebbledoc.toml",
    ".pebbledoc.toml",
    "pyproject.toml",
]


@dataclass(kw_only=True)
class PebbledocConfig:
    """
    Configuration object, holding options specified by the user.
    """

    package_name: str = ""
    source_directory: str | None = None
    output: str = "API.md"
    exclude: list[str] = field(default_factory=list)
    admonition_style: AdmonitionStyle = "mix"
    document_title: str | None = None

    document_constants: bool = True
    module_docstring: bool = True
    include_toc: bool = True
    include_back_to_top: bool = True
    main_module_header: bool = True
    collapsible_params: bool = True
    reference_links: bool = True
    full_toc_name: bool = True


def build_config(args: Namespace) -> PebbledocConfig:
    """
    Build a PebbledocConfig from the command line arguments and config file.

    :param args: The namespace object retrieved from the CLI argparser.
    :return: A PebbledocConfig object, built according to the CLI args.
    """
    # initialize the default config
    config = PebbledocConfig(package_name=args.package)

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
        base_config = loaded_file.get("tool", {}).get("pebbledoc", {})
    else:
        base_config = loaded_file["pebbledoc"]

    # set values if they are given
    for key, value in base_config.items():
        if not hasattr(config, key):
            warnings.warn(
                f"Config parameter '{key}' does not exist in pebbledoc",
                UserWarning,
                stacklevel=2,
            )
            continue
        setattr(config, key, value)
    return _update_for_cli_args(config, args)


def _update_for_cli_args(
    config: PebbledocConfig, args: Namespace
) -> PebbledocConfig:
    """
    Update an existing config file for CLI arguments explicitly given.

    :param config: The existing config object to update.
    :param args: The argparse namespace object retrieved from the CLI.
    :return: The config, with all explicitly provided arguments replaced.
    """
    # overwrite with CLI arguments, if given:
    if args.source_directory is not None:
        config.source_directory = args.source_directory
    if args.output is not None:
        config.output = args.output
    if args.exclude is not None:
        config.exclude = args.exclude
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
        "no_main_module_header": "main_module_header",
        "no_collapsible_params": "collapsible_params",
        "no_references": "reference_links",
        "no_full_toc_name": "full_toc_name",
    }
    for arg_name, config_name in options.items():
        if getattr(args, arg_name):
            setattr(config, config_name, False)

    return config


def _discover_config_file() -> Path | None:
    """
    Ascend from CWD upwards to find nearest config file.

    The function finds the nearest supported pebbledoc config file by
    ascending from the current working directory, and returns it, once
    it finds one. If no such file is found, it returns None.

    :return: Either the path to the nearest valid config file, or None.
    """
    current_dir = Path.cwd()
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
