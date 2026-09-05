# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
while following the version scheme described in the [PyPA version specifiers](https://packaging.python.org/en/latest/specifications/version-specifiers/#version-specifiers)
document, which is based on PEP440.

## Unreleased

### Added

- Option to exclude members from the documentation ([#97](https://github.com/MilanStaffehl/pebbledoc/pull/97))
- Option to disable collapsible info field lists ([#99](https://github.com/MilanStaffehl/pebbledoc/pull/99))
- Option to not render Sphinx-style references as links ([#100](https://github.com/MilanStaffehl/pebbledoc/pull/100))
- Option to create a TOC with shortened member names ([#101](https://github.com/MilanStaffehl/pebbledoc/pull/101))
- Option to remove line wraps (singular line breaks in paragraphs) ([#102](https://github.com/MilanStaffehl/pebbledoc/pull/102))
- Option `--diff` to show changes instead of overwriting file ([#112](https://github.com/MilanStaffehl/pebbledoc/pull/112))
- Option `--exit-code` to emit non-zero exit code when a run changes the docs ([#117](https://github.com/MilanStaffehl/pebbledoc/pull/117))
- Support for using the repo in pre-commit ([#124](https://github.com/MilanStaffehl/pebbledoc/pull/124))
- A generic one-sentence introductory paragraph, and the option to remove it ([#128](https://github.com/MilanStaffehl/pebbledoc/pull/128))
- Option to place the package's main docstring at different locations (before or after TOC, in its section, or omit entirely) ([#128](https://github.com/MilanStaffehl/pebbledoc/pull/128))

### Changed

- Info field lists for parameters, return values, etc. now render as collapsible sections ([#99](https://github.com/MilanStaffehl/pebbledoc/pull/99))
- New dependency `colorama` to color diffs and error messages ([#112](https://github.com/MilanStaffehl/pebbledoc/pull/112))
- If newly generated documentation is identical to the existing one, the old file will no longer be overwritten ([#113](https://github.com/MilanStaffehl/pebbledoc/pull/113))
- Some exit codes have changed ([#119](https://github.com/MilanStaffehl/pebbledoc/pull/119))
- Command line arguments are now grouped differently in help text ([#120](https://github.com/MilanStaffehl/pebbledoc/pull/120))
- Write-only properties no longer receive a superfluous `Any` return type annotation ([#129](https://github.com/MilanStaffehl/pebbledoc/pull/129))
- Option `--no-module-docstring` changed to `--no-module-docstrings` ([#131](https://github.com/MilanStaffehl/pebbledoc/pull/131))
- Option `--no-module-docstrings` now only affects doctrings of submodules and sub-packages ([#131](https://github.com/MilanStaffehl/pebbledoc/pull/131))
- Version notice labels are now bold ([#133](https://github.com/MilanStaffehl/pebbledoc/pull/133))
- "Back to top" links are now placed at the end of sections ([#135](https://github.com/MilanStaffehl/pebbledoc/pull/135))
- Rules for human responsibilities for AI agents in Code of Conduct clarified ([#137](https://github.com/MilanStaffehl/pebbledoc/pull/137))

### Fixed

- Types of constants and class variables are now correctly rendered when a type annotation is given ([#108](https://github.com/MilanStaffehl/pebbledoc/pull/108))
- Type annotations are now correctly rendered for modules without `from __future__ import annotations` ([#108](https://github.com/MilanStaffehl/pebbledoc/pull/108))
- Formatting of help text of command line interface ([#109](https://github.com/MilanStaffehl/pebbledoc/pull/109))
- Multi-line version notices now render properly ([#133](https://github.com/MilanStaffehl/pebbledoc/pull/133))

## [0.1.0] - 2026-08-21

### Added

- Auto-documentation tool for turning RST-documented Python libraries into a
  single-file Markdown document.
- Support for the most common RST features found in docstrings.
- Access to the most useful utilities for programmatic use of `pebbledoc`.
- Documentation in the form of a `README`.
- An overview over supported RST syntax (`FEATURES.md`).
- Guides for contributing (`CONTRIBUTING.md`) and a Code of Conduct.
- License for the project (MIT license).
- This `CHANGELOG` to track future changes to the project.
- A really cute mascot. Look at it!
