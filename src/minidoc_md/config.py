"""
Config object to hold various input options.
"""

from dataclasses import dataclass

from .types import AdmonitionStyle


@dataclass(kw_only=True)
class MinidocConfig:
    package_name: str = ""
    admonition_style: AdmonitionStyle = "mix"
    document_title: str | None = None

    document_constants: bool = True
    module_docstring: bool = True
    include_toc: bool = True
    include_back_to_top: bool = True
    main_module_header: bool = True
