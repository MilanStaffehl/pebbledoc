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

### Changed

- Info field lists for parameters, return values, etc. now render as collapsible sections ([#99](https://github.com/MilanStaffehl/pebbledoc/pull/99))

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
