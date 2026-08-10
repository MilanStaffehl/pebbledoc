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
  - [As a library](#as-a-library)
- [Configuration](#configuration)
  - [Options](#options)
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

`pebbledoc` requires Python 3.13 or higher. You can install `pebbledoc` from PyPI using your preferred package manager. Installation with `uv` into the development dependency group is recommended:

```bash
uv add --dev pebbledoc
```

Alternatively, installation with `pip` is possible as well:

```bash
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

You can run `pebbledoc` directly from your command line. The only required argument is the name of the package you wish to document:

```bash
pebbledoc --package <package_name> [OPTIONS]
```

If you run `pebbledoc` for the first time, test it with the default options to see if you like the output:

```bash
pebbledoc --package my_package
```

This creates a file `API.md` in the current working directory. From there, you can choose to configure `pebbledoc` to your liking using the options. Below is the full listing of command line options; you can display the same text by typing `pebbledoc --help`.

```
usage: pebbledoc [-h] [--version] -p  [-s ] [-o ] [-c ] [--admonition-style {classic,mix,github,map}] [--title ]
                 [--no-module-docstring] [--no-include-constants] [--no-toc] [--no-back-to-top]
                 [--no-main-module-header]

pebbledoc is a lightweight documentation tool - automatically generate a single-file API documentation for your
Python project!

Note that the package you wish to document must either be installed in the same environment as pebbledoc, or you
must specify its source directory when using pebbledoc. Either way, all of its dependencies must be installed.

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -p, --package         name of the package to document
  -s, --source-directory
                        source directory of the package; must be specified if the package is not installed in the
                        current environment
  -o, --output          name and filepath of the output file
  -c, --config-file     file containing pebbledoc configuration instructions, optional
  --admonition-style {classic,mix,github,map}
                        rendering style for admonitions:
                        - classic: render all admonitions as block quotes with headers in bold type
                        - mix: render admonitions supported by GitHub in GitHub style, all others in classic style
                        - github: render all admonitions in GitHub style, as block quotes with headers of the form
                          [!TYPE]
                        - map: render all admonitions in GitHub style, map unsupported admonitions to the closest
                          supported type
  --title               set the title for the document (i.e. its main header)

formatting:
  --no-module-docstring
                        omit module-level docstrings for submodules and sub-packages
  --no-include-constants
                        omit constants defined as module-level globals
  --no-toc              omit the table of contents at the beginning of the file
  --no-back-to-top      omit the 'back to top' links at the beginning of each section
  --no-main-module-header
                        omit the h2 header for the main module
```

For a more in-depth description of the configuration options, see the section on [configuration options](#options) below.

### As a library

In addition to the command line interface, `pebbledoc` also exposes some of its more useful utilities for use in your Python code. To use them, simply import `pebbledoc` in your code using `import pebbledoc`. Run `pebbledoc` on itself to get an overview of the provided utilities:

```bash
pebbledoc --package pebbledoc --output pebbledoc_docs.md
```

## Configuration

You can provide a persistent configuration to `pebbledoc` by creating a configuration file. `pebbledoc` recognizes one of three config file formats:

- `pyproject.toml` (recommended)
- `pebbledoc.toml`
- `.pebbledoc.toml`

All files follow the same format; only the section header is different: For `pyproject.toml`, the section header must be `[tools.pebbledoc]`, while for dedicated configuration files, the section header must be `[pebbledoc]`.

The example below shows a full configuration file, showing all available options.

```toml
# pyproject.toml

[tools.pebbledoc]
package_name = "my_package"
admonition_style = "mix"
document_title = "My Package - documentation"
document_constants = true
module_docstring = true
include_toc = true
include_back_to_top = true
main_module_header = true
```

### Options

The following table shows how the configuration options map to the command line flags. For a description of what the options are, see the help text of the corresponding command line option in [Command line usage](#command-line-usage).

| Config key            | CLI flag                  | Notes                                                         |
|-----------------------|---------------------------|---------------------------------------------------------------|
| `package_name`        | `--package`               | Also used as the document title if `document_title` isn't set |
| `admonition_style`    | `--admonition-style`      | See [Admonitions](#admonitions) for details on each style     |
| `document_title`      | `--title`                 | Overrides the default title derived from `package_name`       |
| `document_constants`  | `--no-include-constants`  |                                                               |
| `module_docstring`    | `--no-module-docstring`   |                                                               |
| `include_toc`         | `--no-toc`                |                                                               |
| `include_back_to_top` | `--no-back-to-top`        |                                                               |
| `main_module_header`  | `--no-main-module-header` |                                                               |

### Admonitions

GitHub-flavored Markdown supports five tyes of admonitions (or ["alerts"](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#alerts) as GitHub calls them): Caution, Warning, Important, Note, and Tip. These are automatically rendered on GitHub with colorful boxes and icons. However, resStructuredText offers more than these five admonition types. The `admonition_style` config option determines what to do with these additional admonition types. The options are as follows:

- `classic`: All admonitions, including those supported by GitHub, are formatted as block quotes, preceded with the admonition type name in bold face at the top. In this style, the GitHub rendering feature is not used at all.
- `github`: All admonitions, including the unsupported ones, are formatted using the GitHub-flavored syntax (beginning with the admonition type name in all caps, preceded by an exclamation mark, in brackets). This may look odd for admonition types not supported by GitHub, but the supported admonition types are rendered correctly.
- `mix`: This is the default style. It leaves the five supported admonition styles in GitHub syntax, causing them to be rendered as colorful boxes, while formatting all unsupported types in `classic` style. This leaves inconsistent styles, but offers a visually pleasant compromise.
- `map`: All unsupported admonition types are mapped to the closest supported type, then formatted as GitHub-flavored alerts. This results in all admonitions being rendered as alerts, albeit not necessarily with their original type. The mapping from admonitions to alerts is as follows:
  - `attention` $\to$ `important`
  - `danger` $\to$ `caution`
  - `error` $\to$ `caution`
  - `hint` $\to$ `tip`
  - `admonition` (general admonition) $\to$ `note` (custom titles are lost)

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
