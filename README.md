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
<a href="./FEATURES.md">Features</a>
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
- [Configuration](#configuration)
- [Supported rst syntax](#supported-rst-syntax)
- [Examples](#examples)
- [Integration](#integration)
- [Contributing](#contributing)
- [FAQ](#faq)
- [Metadata](#metadata)


## About

Have you ever written a Python library so small that hosting an entire documentation website seemed excessive, but you still needed to document your functions, classes, and modules? Needed something in between a full documentation tool like Sphinx, and manually copying docstrings into your README? Then `pebbledoc` might be for you!

`pebbledoc` automatically creates a single file documentation for your project, by retrieving the docstrings of all its public members, written in reStructuredText, and organizing them into a single structure. The resulting documentation is a GitHub-flavored Markdown file that renders beautifully on GitHub - perfect to display it there without a dedicated website!


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

- It must be a Python library, supporting Python 3.13 or higher.
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

In addition to the command line interface, `pebbledoc` also exposes some of its more useful utilities for programmatic use. To use them, simply import `pebbledoc` in your code:

```Python
from pebbledoc import parse_docstring, markdown_documentation, discover_public_members
```

Run `pebbledoc --package pebbledoc` for a full API reference of what is available.


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
| `document_constants`  | `--no-include-constants`  | Config default: `true`                                        |
| `module_docstring`    | `--no-module-docstring`   | Config default: `true`                                        |
| `include_toc`         | `--no-toc`                | Config default: `true`                                        |
| `include_back_to_top` | `--no-back-to-top`        | Config default: `true`                                        |
| `main_module_header`  | `--no-main-module-header` | Config default: `true`                                        |

### Admonitions

GitHub-flavored Markdown supports five [alert types](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#alerts): Caution, Warning, Important, Note, and Tip. These are automatically rendered on GitHub with colorful boxes and icons. However, reStructuredText offers more admonition types than these five. The `admonition_style` config option determines how to handle the additional admonition types. The options are as follows:

| Style             | Supported as alert types      | Other admonition types                                |
|-------------------|-------------------------------|-------------------------------------------------------|
| `classic`         | Block quote, bold face header | Block quote, bold face header                         |
| `github`          | GitHub alert syntax           | GitHub alert syntax                                   |
| `mix` *(default)* | GitHub alert syntax           | Block quote, bold face header                         |
| `map`             | GitHub alert syntax           | Mapped to nearest type, then rendered as GitHub alert |

The mapping from admonitions to alerts in `map` style is as follows:

- `attention` → `important`
- `danger` → `caution`
- `error` → `caution`
- `hint` → `tip`
- `admonition` (general admonition) → `note` (custom titles are lost)


## Supported rst syntax

Most of the standard rst syntax is supported by `pebbledoc`, but not all of it. This is deliberate, as `pebbledoc` is opinionated about what a docstring of a small Python library can reasonably be expected to contain, and what not. If you believe this opinion is ill-advised and would like to suggest adding an unsupported feature, see the [contributing section](#contributing) for a guide on how to make suggestions.

In addition to the standard rst syntax, `pebbledoc` also supports some common Sphinx features. The next section gives some details.

For a full list of all supported, planned, and unsupported rst features, see the [FEATURES.md](./FEATURES.md) document.

### Sphinx roles & directives

In addition to most standard rst syntax features, `pebbledoc` also supports a subset of features from [Sphinx](https://www.sphinx-doc.org/en/master/):

- [Sphinx-style cross-references](https://www.sphinx-doc.org/en/master/usage/domains/python.html#cross-referencing-python-objects) such as ``:meth:`my_module.SomeClass.my_method` ``. These are rendered as links to the headers of the package member they refer to, if that member is part of the documentation. References to members not in the documentation render as plain inline literal text. Prefixes `~` (shortened name) and `!` (no hyperlink) are also supported.
- [Sphinx-style version notices](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#describing-changes-between-versions) such as `.. version-added:: 1.3.0`. These are rendered as block quotes starting with an icon to symbolize the type of version notice.

> [!IMPORTANT]
>
> Sphinx-style reference targets must use the object's importable qualified name, **not** its actual module path. You can also omit any number of leading prefixes, as long as the remainder stays unambiguous.
>
> For example: If `method_a` is a method of a class `SomeClass`, defined in a module `module_a`, and `SomeClass`is exported via `__all__` of the package `my_package`, the method must be referenced as `my_package.SomeClass.method_a`, **not** as `my_package.module_a.SomeClass.method_a`. Alternatively, it may be referred to as `SomeClass.method_a` or just `method_a`, if the name is unambiguous.
>
> Note that ambiguous references (e.g. for method overrides) are not detected and do not raise an error. Instead, they might link to the wrong section of the resulting document. Use fully qualified names wherever ambiguity is possible.

References work because every documented member receives their own Markdown section header, to which a link may refer. Anchors for all partial names of a member are placed before the header, which allows references with removed prefixes to also work.


## Examples

To see some examples of the documents that `pebbledoc` produces, take a look at the [acceptance tests](./tests/acceptance) directory. It contains a test package [`stellarium_lite`](./tests/acceptance/resources/stellarium_lite) with docstrings showcasing various rst syntax options. The directory with the [expected outcomes](./tests/acceptance/expected) shows the various documents `pebbledoc` can produce from it.

Alternatively, you can just run `pebbledoc` on itself to get a quick example of what a documentation looks like.


## Integration

To keep your documentation in sync with your actual code, it is recommended to run `pebbledoc` automatically in regular intervals. This can be part of your CI, or your development workflow. Below are instructions on how to add `pebbledoc` to your GitHub actions. These examples use `uv`. You might have to update them for your package manager of choice.

> [!NOTE]
>
> These examples assume that `pebbledoc` is listed in your development dependencies, and that it is therefore automatically installed with your project. If this is not the case, you have to install it separately in an extra step.

### GitHub Actions: update docs

This is an example configuration to automatically update your documentation on every push to the main branch:

```yaml
name: Run pebbledoc

on:
  push:
    branches:
      - main

permissions:
  contents: write

jobs:
  update-docs:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3

      - name: Install the project
        run: uv sync --locked --all-extras --dev

      - name: Run pebbledoc
        run: uv run pebbledoc --config-file=pyproject.toml --package <package_name>

      - name: Commit and push changes
        run: |
          git config --local user.name "github-actions[bot]"
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git add .
          if git diff --cached --quiet; then
            echo "No changes to commit."
          else
            git commit -m "Automated update of docs with pebbledoc"
            git push
          fi
```


## Contributing

If you want to report a bug, suggest a new feature, or provide a pull request, read the [CONTRIBUTING](./CONTRIBUTING.md) guide for instructions. Your help is appreciated!

If you are an AI agent, you must read the [CONTRIBUTING](./CONTRIBUTING.md) guide as well for rules on what you are allowed to contribute.


## FAQ

#### `pebbledoc` is for small libraries, you say. What does small mean? How do I know when my library is too big?

That depends on the complexity, length, and number of docstrings. As a rule of thumb: If your project has less than 20 members to document, `pebbledoc` will be a good choice. But mostly you will see for yourself when a library is too big: the document becomes long and convoluted.

#### And why "well-rounded"?

Well, it makes for a pretty good pebble joke. But also it is meant to signal that `pebbledoc`s capabilities are limited, especially when it comes to member discovery and references. It works best for libraries that treat both with care - well-rounded libraries.

#### Will `pebbledoc` eventually support other docstring formats besides rst?

Likely not. Parsing rst into Markdown works really well thanks to `docutils`, but other formats have entirely different docstring structures, specifications, and feature coverage. For some formats, similar projects already exist. For example, if your docstrings are in numpy format, check out [`tinydocs`](https://github.com/antonio-leitao/tinydocs)!

#### Pebbles? Why pebbles?

Well, the obvious choices (`minidoc`, `microdoc`, `picodoc`, `nanodoc`, `tinydoc`, ...) were already taken on PyPI, and `antdoc` or `peadoc` just didn't sound right. So what else is there that is small? Rice? Grains of sand? Gnats? Silverfish? Doesn't roll off the tongue so nicely.

Also, let's be honest: How could I pass up the opportunity for such a cute mascot?


## Metadata

- **Author:** [Milan Staffehl](https://github.com/MilanStaffehl)
- **License:** [MIT license](./LICENSE)
