"""
Config object to hold various input options.
"""

from dataclasses import dataclass

from .types import AdmonitionStrategy


@dataclass(kw_only=True)
class MinidocConfig:
    package_name: str = ""
    admonition_strategy: AdmonitionStrategy = "mix"
    document_title: str | None = None

    document_constants: bool = True
    module_docstring: bool = True
    include_toc: bool = True
    include_back_to_top: bool = True
