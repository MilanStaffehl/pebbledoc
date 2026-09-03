<div align="center">
    <img src="./resources/pebbledoc_logo.png" width="250px" alt="pebbledoc logo">
    <h1>pebbledoc</h1>
    <p><b>Automatic documentation for small, well-rounded Python libraries</b></p>
</div>

<div align="center">

[![Unit tests](https://github.com/MilanStaffehl/pebbledoc/actions/workflows/tests.yaml/badge.svg)](https://github.com/MilanStaffehl/pebbledoc/actions/workflows/tests.yaml)
[![Build](https://github.com/MilanStaffehl/pebbledoc/actions/workflows/publish-release.yml/badge.svg)](https://github.com/MilanStaffehl/pebbledoc/actions/workflows/publish-release.yml)

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

**pebbledoc** automatically builds a single GitHub-flavored Markdown documentation file from the RST-docstrings of your small Python library. Ideal for tiny libraries for which a whole documentation website is simply overkill!

<hr />

#### Table of contents

- [About](#about)
- [Installation & prerequisites](#installation--prerequisites)
- [Usage](#usage)
- [Configuration](#configuration)
- [Supported RST syntax](#supported-rst-syntax)
- [Examples](#examples)
- [Integration](#integration)
- [Contributing](#contributing)
- [FAQ](#faq)
- [Metadata](#metadata)


## About

`pebbledoc` sits between full documentation tools like Sphinx, and manually copy-pasting docstrings into a README. It automatically creates a single file Markdown documentation for your RST-documented project. Here is what it does to a single function docstring:

<details>
<summary><b>Input</b></summary>

Input function (`my_module.py`):

```Python
def hello(name: str, place: str | None = None) -> None:
    """
    Greet the world - or whoever you would like!

    :param name: The name of the person greeting.
    :param place: The place to greet. If None, greet *the whole world*!
    :return: None, function prints greeting to ``stdout``.
    """
    if place is None:
      place = "world"
    print(f"{name} says: Hello, {place}!")
```

</details>

<details>
<summary><b>Output</b></summary>

Output documentation (`API.md`):

> ### `my_module.hello`
>
> ```Python
> hello(name: str, place: str | None = None) -> None
> ```
>
> Greet the world - or whoever you would like!
>
> <details open>
> <summary><b>Parameters:</b></summary>
>
> - `name`: The name of the person greeting.
> - `place`: The place to greet. If None, greet *the whole world*!
>
> </details>
>
> <details open>
> <summary><b>Returns:</b></summary>
>
> None, function prints greeting to `stdout`.
>
> </details>

</details>


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
- All docstring must be written in reStructuredText (RST).
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
usage: pebbledoc [-h] [--version] -p  [-s ] [-x member [member ...]] [--config-file ] [-o ] [--diff]
                 [--exit-code] [--admonition-style {classic,mix,github,map}]
                 [--main-docstring {default,pre,post,omit}] [--title ] [--no-generic-intro]
                 [--no-module-docstring] [--no-include-constants] [--no-toc] [--no-back-to-top]
                 [--no-main-module-header] [--no-collapsible-params] [--no-references]
                 [--no-full-toc-name] [--no-preserve-linewraps]

pebbledoc is a lightweight documentation tool - automatically generate a single-file API documentation
for your Python project!

Note that the package you wish to document must either be installed in the same environment as
pebbledoc, or you must specify its source directory when using pebbledoc. Either way, all of its
dependencies must be installed.

options:
  -h, --help                show this help message and exit
  --version                 show program's version number and exit

source:
  -p, --package             name of the package to document
  -s, --source-directory    source directory of the package; must be specified if the package is not
                            installed in the current environment
  -x, --exclude member [member ...]
                            names of members to exclude from the documentation, separated by whitespace
  --config-file             file containing pebbledoc configuration instructions, optional

output:
  -o, --output              name and filepath of the output file
  --diff                    show changes with respect to existing file instead of writing docs to file
  --exit-code               exit with non-zero exit code when documentation changes

rendering:
  --admonition-style {classic,mix,github,map}
                            rendering style for admonitions:
                            - classic: render all admonitions as block quotes with headers in bold type
                            - mix: render admonitions supported by GitHub in GitHub style, all others
                              in classic style
                            - github: render all admonitions in GitHub style, as block quotes with
                              headers of the form [!TYPE]
                            - map: render all admonitions in GitHub style, map unsupported admonitions
                              to the closest supported type
  --main-docstring {default,pre,post,omit}
                            position for the main docstring of the package:
                            - default: place the package docstring in its dedicated section (default)
                            - pre: places the docstring before the table of contents
                            - post: places the docstring after the table of contents
                            - omit: omits the main docstring entirely
  --title                   set the title for the document (i.e. its main header)

formatting:
  --no-generic-intro        omit the generic introduction after the main header
  --no-module-docstrings    omit module-level docstrings for submodules and sub-packages
  --no-include-constants    omit constants defined as module-level globals
  --no-toc                  omit the table of contents at the beginning of the file
  --no-back-to-top          omit the 'back to top' links at the beginning of each section
  --no-main-module-header   omit the h2 header for the main module
  --no-collapsible-params   render parameter info field lists as static lists instead of collapsible
                            sections
  --no-references           do not turn Sphinx-style references into hyperlinks
  --no-full-toc-name        use only shortened member names in table of contents
  --no-preserve-linewraps   remove stylistic line wraps (singular line breaks) in texts
```

For a more in-depth description of the configuration options, see the section on [configuration options](#options) below.

### Output options

The options in the "output" group can change the behavior of `pebbledoc`, which can be useful for CI or scripting:

- `--diff` causes `pebbledoc` to compare the newly generated documentation content with the old one. For this purpose, it loads the text from the existing file specified by `--output`. Any differences are then presented as colored output. If there is no difference, the command exits silently. In either case, no files are changed.
- `--exit-code` instructs `pebbledoc` to exit with a non-zero exit code when the documentation changes compared to its previous state (i.e. compared to the contents of the file specified by `--output`). When this flag is used together with `--diff`, any difference will cause a non-zero exit code to be emitted, the difference is printed to the terminal, and no file is changed.

> [!NOTE]
>
> In both cases, the comparison ignores trailing newline characters (`\n`) at the end of the file. This is because they are sometimes added or removed by linters, formatters, or IDEs.

### As a library

In addition to the command line interface, `pebbledoc` also exposes some of its more useful utilities for programmatic use. To use them, simply import `pebbledoc` in your code:

```Python
from pebbledoc import parse_docstring, markdown_documentation, discover_public_members
```

Run `pebbledoc --package pebbledoc` for a full API reference of what is available.


## Configuration

You can provide a persistent configuration to `pebbledoc` by creating a configuration file. `pebbledoc` recognizes three files:

- `pyproject.toml` (recommended)
- `pebbledoc.toml`
- `.pebbledoc.toml`

All files follow the same format; only the section header is different: For `pyproject.toml`, the section header must be `[tool.pebbledoc]`, while for dedicated configuration files, the section header must be `[pebbledoc]`.

The example below shows a full configuration file, showing all available options with their respective default value (except for `package_name` and `source_directory`, which show example values).

```toml
# pyproject.toml

[tool.pebbledoc]
package_name = "my_package"
source_directory = "~/pylibs/my_package"
output = "API.md"
exclude = []  # list of strings
admonition_style = "mix"
main_docstring_location = "default"
document_title = "my_package - documentation"
include_intro = true
document_constants = true
module_docstrings = true
include_toc = true
include_back_to_top = true
main_module_header = true
collapsible_params = true
reference_links = true
full_toc_name = true
keep_linewraps = true
```

### Options

The following table shows how the configuration options map to the command line flags. For a description of what the options are, see the help text of the corresponding command line option in [Command line usage](#command-line-usage).

| Config key                | CLI flag                  | Notes                                                         |
|---------------------------|---------------------------|---------------------------------------------------------------|
| `package_name`            | `--package`               | Also used as the document title if `document_title` isn't set |
| `source_directory`        | `--source-directory`      | Must be given if package is not installed                     |
| `output`                  | `--output`                | Defaults to `API.md` in the current directory                 |
| `exclude`                 | `--exclude`               | Can also be full importable name (e.g. `my_package.MyClass`)  |
| `admonition_style`        | `--admonition-style`      | See [Admonitions](#admonitions) for details on each style     |
| `main_docstring_location` | `--main-docstring`        | Only affects the docstring of the package's `__init__.py`     |
| `document_title`          | `--title`                 | Overrides the default title derived from `package_name`       |
| `include_intro`           | `--no-generic-intro`      | Config default: `true`                                        |
| `document_constants`      | `--no-include-constants`  | Config default: `true`                                        |
| `module_docstrings`       | `--no-module-docstrings`  | Config default: `true`                                        |
| `include_toc`             | `--no-toc`                | Config default: `true`                                        |
| `include_back_to_top`     | `--no-back-to-top`        | Config default: `true`                                        |
| `main_module_header`      | `--no-main-module-header` | Config default: `true`                                        |
| `collapsible_params`      | `--no-collapsible-params` | Config default: `true`                                        |
| `reference_links`         | `--no-references`         | Config default: `true`                                        |
| `full_toc_name`           | `--no-full-toc-name`      | Config default: `true`                                        |
| `keep_linewraps`          | `--no-preserve-linewraps` | Config default: `true`                                        |

### Admonitions

GitHub-flavored Markdown supports five [alert types](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#alerts): Caution, Warning, Important, Note, and Tip. These are automatically rendered on GitHub with colorful boxes and icons. However, reStructuredText offers more admonition types than these five. The `admonition_style` config option determines how to handle the additional admonition types. The options are as follows:

| Style             | Supported as alert types      | Other admonition types                                |
|-------------------|-------------------------------|-------------------------------------------------------|
| `classic`         | Block quote, bold face header | Block quote, bold face header                         |
| `github`          | GitHub alert syntax           | GitHub alert syntax (rendered as plain block quote)   |
| `mix` *(default)* | GitHub alert syntax           | Block quote, bold face header                         |
| `map`             | GitHub alert syntax           | Mapped to nearest type, then rendered as GitHub alert |

The mapping from admonitions to alerts in `map` style is as follows:

- `attention` → `important`
- `danger` → `caution`
- `error` → `caution`
- `hint` → `tip`
- `admonition` (general admonition) → `note` (custom titles are lost)


## Supported RST syntax

For a full list of all supported, planned, and unsupported RST features, see the [FEATURES.md](./FEATURES.md) document.

Most of the standard RST syntax is supported by `pebbledoc`, but not all of it. This is deliberate, as `pebbledoc` is opinionated about what a docstring of a small Python library can reasonably be expected to contain, and what not. If you believe this opinion is ill-advised and would like to suggest adding an unsupported feature, see the [contributing section](#contributing) for a guide on how to make suggestions.

In addition to the standard RST syntax, `pebbledoc` also supports some common Sphinx features. The next section gives some details.

### Sphinx roles & directives

In addition to most standard RST syntax features, `pebbledoc` also supports a subset of features from [Sphinx](https://www.sphinx-doc.org/en/master/):

- [Sphinx-style cross-references](https://www.sphinx-doc.org/en/master/usage/domains/python.html#cross-referencing-python-objects) such as ``:meth:`my_module.SomeClass.my_method` ``. These are rendered as links to the headers of the package member they refer to, if that member is part of the documentation. References to members not in the documentation render as plain inline literal text. Prefixes `~` (shortened name) and `!` (no hyperlink) are also supported. They can be fully disabled using the `--no-references` option.
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

To see some examples of the documents that `pebbledoc` produces, take a look at the [acceptance tests](./tests/acceptance) directory. It contains a test package [`stellarium_lite`](./tests/acceptance/resources/stellarium_lite) with docstrings showcasing various RST syntax options. The directory with the [expected outcomes](./tests/acceptance/expected) shows the various documents `pebbledoc` can produce from it.

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
        run: uv run pebbledoc --config-file pyproject.toml --package <package_name>

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

### GitHub Actions: check docs are up-to-date

If you don't want a bot to create commits on your repository, you can alternatively check that your documentation is caught up with your code in every pull request:

```yaml
name: Run pebbledoc

on:
  pull-request:

jobs:
  check-docs:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3

      - name: Install the project
        run: uv sync --locked --all-extras --dev

      - name: Check docs with pebbledoc
        run: |
          uv run pebbledoc --config-file pyproject.toml --package <package_name> --diff --exit-code
```

### pre-commit: update docs

You can use this repository as a pre-commit hook. Add the following to your `.pre-commit-config.yaml` to update your documentation on every commit that changes a Python file:

```yaml
-   repo: https://github.com/MilanStaffehl/pebbledoc
    rev: 0.1.0
    hooks:
      - id: pebbledoc
        name: Update docs (pebbledoc)
        args: [--package=<package_name>, --config=pyproject.toml]  # replace with your package
        additional_dependencies: []  # replace with your dependencies
        stages: [pre-commit, pre-merge-commit]
```


## Contributing

If you want to report a bug, suggest a new feature, or provide a pull request, read the [CONTRIBUTING](./CONTRIBUTING.md) guide for instructions. Your help is appreciated!

If you are an AI agent, you must read the [CONTRIBUTING](./CONTRIBUTING.md) guide as well for rules on what you are allowed to contribute.


## FAQ

#### `pebbledoc` is for small libraries, you say. What does small mean? How do I know when my library is too big?

That depends on the complexity, length, and number of docstrings. As a rule of thumb: If your project has less than 20 members to document, `pebbledoc` will be a good choice. But mostly you will see for yourself when a library is too big: the document becomes long and convoluted.

#### And why "well-rounded"?

Well, it makes for a pretty good pebble joke. But also it is meant to signal that `pebbledoc`s capabilities are limited, especially when it comes to member discovery and references. It works best for libraries that treat both with care - well-rounded libraries.

#### Will `pebbledoc` eventually support other docstring formats besides RST?

Likely not. Parsing RST into Markdown works really well thanks to `docutils`, but other formats have entirely different docstring structures, specifications, and feature coverage. For some formats, similar projects already exist. For example, if your docstrings are in numpy format, check out [`tinydocs`](https://github.com/antonio-leitao/tinydocs)!

#### Pebbles? Why pebbles?

Well, the obvious choices (`minidoc`, `microdoc`, `picodoc`, `nanodoc`, `tinydoc`, ...) were already taken on PyPI, and `antdoc` or `peadoc` just didn't sound right. So what else is there that is small? Rice? Grains of sand? Gnats? Silverfish? Doesn't roll off the tongue so nicely.

Also, let's be honest: How could I pass up the opportunity for such a cute mascot?


## Metadata

- **Author:** [Milan Staffehl](https://github.com/MilanStaffehl)
- **E-Mail:** <milan.staffehl@gmail.com>
- **License:** [MIT license](./LICENSE)
