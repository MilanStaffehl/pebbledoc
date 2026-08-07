<div align="center">
    <img src="./resources/pebbledoc_logo.png" width="250px" alt="pebbledoc logo">
    <h1>pebbledoc</h1>
    <p><b>Automatic documentation for small, well-rounded Python libraries</b></p>
</div>

<div align="center">

[![Unit tests](https://github.com/MilanStaffehl/pebbledoc/actions/workflows/tests.yaml/badge.svg)](https://github.com/MilanStaffehl/pebbledoc/actions/workflows/tests.yaml)

<a href="https://github.com/MilanStaffehl/pebbledoc">GitHub</a>
·
<a href="https://pypi.org/project/pebbledoc/">PyPI</a>
·
<a href="./tests/acceptance/expected">Examples</a>
·
<a href="./FFEATURES.md">Features</a>
·
<a href="./CONTRIBUTING.md">Contributing</a>
·
<a href="./CHANGELOG.md">Changelog</a>

</div>

**pebbledoc** automatically builds a single GitHub-flavored Markdown documentation file from the rst-docstrings of your small Python library. Ideal for tiny libraries for which a whole documentation website is simply overkill!

<hr />

#### Table of contents

- [About](#about)
- [Installation & prerequisites](#installation--prerequisites)
- [Usage](#usage)
  - [Command line usage](#command-line-usage)
  - [Admonitions](#admonitions)
  - [Sphinx roles & directives](#sphinx-roles--directives)
- [Supported rst syntax](#supported-rst-syntax)
- [Limitations & caveats](#limitations--caveats)
- [Examples](#examples)
- [Integration](#integration)
  - [pre-commit](#pre-commit)
  - [GitHub Actions](#github-actions)
- [Contributing](#contributing)
- [FAQ](#faq)

## About

## Installation & prerequisites

`pebbledoc` requires Python 3.13 or higher. You can install `pebbledoc` from PyPI using your preferred package manager. Installation with `uv` is recommended:

```shell
uv add pebbledoc
```

Alternatively, installation with `pip` is possible as well:

```shell
pip install pebbledoc
```

To be able to use `pebbledoc`, the project you wish to document must meet the following requirements:

- It must be a Python library, supporting Python 3.12 or higher.
- It must either provide `__all__` in all packages, or explicitly re-export members of its API in the package's `__init__.py`.
- All docstring must be written in reStructuredText (rst).
  - They *can* also contain certain Sphinx-specific syntax, see [supported syntax](#supported-rst-syntax) for details.
- `pebbledoc` and all your project's dependencies must be installed in the same environment.

## Usage

### Command line usage

### Admonitions

### Sphinx roles & directives

## Supported rst syntax

## Limitations & caveats

## Examples

## Integration

### pre-commit

### GitHub Actions

## Contributing

## FAQ

## Matadata

- **Author:** [Milan Staffehl](https://github.com/MilanStaffehl)
- **License:** [MIT license](./LICENSE)
