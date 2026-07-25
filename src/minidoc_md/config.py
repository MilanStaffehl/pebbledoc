"""
Config object to hold various input options.
"""

from dataclasses import dataclass

from .types import AdmonitionStrategy


@dataclass
class MinidocConfig:
    admonition_strategy: AdmonitionStrategy = "mix"

    document_constants: bool = True
    module_docstring: bool = True
