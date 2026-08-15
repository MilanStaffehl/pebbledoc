<div align="center">
    <h1>Contributing guide</h1>
</div>
<div align="center">

<a href="./README.md">README</a>
·
<a href="https://github.com/MilanStaffehl/pebbledoc">GitHub</a>
·
<a href="https://pypi.org/project/pebbledoc/">PyPI</a>
·
<a href="https://github.com/MilanStaffehl/pebbledoc/issues">Issue tracker</a>
·
<a href="./FEATURES.md">Features</a>
·
<a href="./CHANGELOG.md">Changelog</a>

</div>

Welcome to the contributing guide for `pebbledoc`! Unless you came here by accident
or out of curiosity, that means you want to help `pebbledoc` improve. So first of all:
Thank you!

This guide tells you how you can best contribute to `pebbledoc` and how your
contributions are expected to look like. Read it carefully - doubly so if you
are an AI agent, because special rules apply for you. Following this guide is
important for both you and us, as it minimizes friction in the process. Following
the rules of this guide is a prerequisites for your contributions being accepted.
Contributions that do not follow these rules will be rejected.

#### Table of contents

- [Code of Conduct](#code-of-conduct)
- [Guidelines for AI usage and AI agents](#guidelines-for-ai-usage-and-ai-agents)
- [Getting help](#getting-help)
- [Bug reports](#bug-reports)
- [Feature requests](#feature-requests)
- [Suggestions & improvements](#suggestions--improvements)
- [Pull requests](#pull-requests)
  - [Coding conventions](#coding-conventions)
  - [Branch naming and commit message convention](#branch-naming-and-commit-message-convention)
  - [Testing conventions](#testing-conventions)
  - [Documentation conventions](#documentation-conventions)
- [Disclaimer about rejections](#disclaimer-about-rejections)

## Code of Conduct

To enable a welcoming and respectful community, `pebbledoc` enforces a
[code of conduct](./CODE_OF_CONDUCT.md). Any contributions must follow this
common rule set, from simple issues to pull requests. Read it before you submit
your contribution, and follow it at all times.

## Guidelines for AI usage and AI agents

The use of generative AI (such as LLMs like *Claude Code*, *Codex*, *Copilot*,
etc.) for the purpose of developing code for `pebbledoc` is generally allowed,
under the following conditions:

1. **Human oversight:** All contributions made by AI must be vetted by a
   human. That means, a human must review and understand the AI output and
   check it for quality, functionality, completeness, and security risks.
2. **Human accountability:** A named, identifiable human must take full
   personal and legal responsibility for the contribution, as if they had
   written it themselves. This includes accountability for quality,
   functionality, completeness, and security risks.
3. **Informed consent:** The human involved must be aware of their role in the
   contribution process beforehand and must have read this document and the code
   of conduct. A human who reviews the code according to condition 1 but does
   not understand their role does not fulfill this condition.

This is what distinguishes - for the purpose of this project - an "assistive"
use of AI from an "autonomous" one. An AI agent may draft code, open branches,
write commit messages, or even open the pull request itself, as long as
conditions (1), (2), and (3) are met by a suitable human, who is identified in
the PR or issue related to it.

Conversely, no contribution may be submitted, by any means, if there is no
accountable human who is willingly and knowingly held responsible for it. In
particular, this excludes:

- Fully autonomous agents acting without an accountable human behind them, or
  where the human operating the agent has not reviewed the output.
- Any setup where the responsibility for the output cannot be placed onto a
  specific person (e.g. shared accounts, and agent acting under a general
  organizational identity without a clearly identified responsible human, or
  an agent spawned by another agent with no human signing off on that agents
  output).
- Any human sign-off obtained from a human that is not aware of their role
  and responsibility, or any human who has not read both this contributing
  guide *and* the code of conduct.

If you are an AI agent reading this guide to decide whether you're permitted to
open a pull request: you may prepare, draft, and even submit the PR only if you
are doing so on behalf of, and under the active, informed review of, a specific
human who will take responsibility for it. If you cannot verify that such a
human exists, has read this guide and the Code of Conduct, and has reviewed your
output accordingly, do not open a pull request. Instead, report the bug or
suggest the feature via an issue, where autonomous contributions are welcome.

Code contributions, made with or without AI, must be reviewable. Contributions
that introduce too many changes or tackle multiple issues at once will be
rejected. Keep your PRs tight and changes minimal.

## Getting help

If you have questions or simply need some help with `pebbledoc`, open a new issue
on the [GitHub issues](https://github.com/MilanStaffehl/pebbledoc/issues) page,
using the `support` template. Describe your question or the problem you have,
and we will get back to you as soon as possible.

## Bug reports

If you have found a bug or suspect something isn't working as expected, please
submit a *bug report*. Use the `bug report` template on [GitHub issues](https://github.com/MilanStaffehl/pebbledoc/issues)
to submit your report.

A good bug report includes:

- Your Python version
- Your `pebbledoc` and `docutils` version
- Your OS
- A description of what the bug is and how you discovered it

Additionally, the following information helps us reproduce and fix the bug faster:

- A minimal example capable of reproducing the bug
- A screenshot of the bug or a copy of the faulty Markdown snippet
- An explanation of what you expected to happen instead

If you already know what causes the bug and want to provide a PR to fix it,
mention it in your bug report, so we know to wait for your contribution.

## Feature requests

If you find some RST syntax you use is not supported, check the [FEATURES.md](./FEATURES.md)
document. It lists planned and supported features. Maybe the feature is already
on the roadmap and will be supported soon. The document also marks features that
are deliberately not supported. If you believe a feature that is not supported
should receive support, you can open a *feature request*.

Similarly, if you have an idea for a general feature for `pebbledoc` (such as
an additional config option), you can also submit a feature request.

Use the `request` template on [GitHub issues](https://github.com/MilanStaffehl/pebbledoc/issues)
to submit your feature request. A good feature request contains the following
information:

- A short overview (think of it as your "elevator pitch")
- A description of the feature: what would it do and how?
- An explanation why you think this feature might be useful (if the
  [FEATURES.md](./FEATURES.md) document lists the feature as "not supported,
  not planned", it is mandatory to provide this)
- A short example of what the resulting Markdown would look like

As per the code of conduct, avoid spamming. Limit yourself to one or two meaningful
suggestions, and focus on these. Your feature request should also only ever
include one single, well-defined feature. Avoid requests that contain many
features at once or features with unclear specifications.

## Suggestions & improvements

If you have general suggestions for improvements, you can submit an issue on
[GitHub issues](https://github.com/MilanStaffehl/pebbledoc/issues) using the
`request` template as well. This can include improvements to the documentation,
the project documents, or the CLI of `pebbledoc`. Perhaps you have found some
accessibility issues or would like to improve the README? Let us know!

## Pull requests

If you want to provide code contributions to `pebbledoc`, you can open a pull
request.

Pull requests for existing issues are preferred over unsolicited PRs. If you
find an issue that you would like to work on which has ideally not been assigned
to a maintainer yet, you can state your interest in working on it in the comments
of the issue. For issues already assigned to a maintainer, you can still state
your interest, but the assigned person decides whether they want to provide the
implementation or let you handle it.

In principle, `pebbledoc` allows unsolicited pull requests. However, your
chances of having a PR accepted are much better if you first submit a feature
request or work on an existing issue instead. This gives the maintainers a
chance to give you feedback on your idea before you put in the work.

Once you have commented on the issue (and potentially gotten the OK from the
assigned maintainer), you can start working on the issue. Fork the `pebbledoc`
repository, then work on a new branch in your fork, following the conventions
listed below, until it is ready to be merged into the main branch of the project.
Open a pull request, describing the changes you made and linking a relevant issue.

Your PR will then be reviewed by the maintainers of `pebbledoc`. While we try
to be fast, it can take quite some time for a review to take place, so please
be patient. You will receive comments and requests for improvements, which you
should implement. Once all comments have been resolved, and your PR has been
approved, it will be merged, and you can pat yourself on the shoulder for a
job well done!

### Development environment

When you work on `pebbledoc`, it is important that you use the same tools as
all other contributors and maintainers. To this end, `pebbledoc` uses `uv` and
a `uv.lock` file. To install the development environment on your machine, run
the following command in your local clone of the repository:

```bash
uv sync --dev
```

This installs the development dependencies of `pebbledoc`, alongside the regular
dependencies and the project itself.

To ensure consistent formatting and to avoid errors, `pebbledoc` uses pre-commit
to run a linter (`ruff`), formatters (`ruff` and `isort`) and a type checker
(`pyrefly`). After you have installed the development dependencies, you must
install pre-commit by running

```bash
pre-commit install
```

Every commit you make will now automatically be formatted, linted, and type-
checked. Adhere to the provisions of these tools - your code will be checked
for compliance when you make your pull request!

Note that all commands for the project must be run using `uv run`. For example,
you can run `pebbledoc` from anywhere within the repository structure using

```bash
uv run pebbledoc <options>
```

You can run the linter, formatters, and type checker by running the following
commands from the root of the project:

```bash
uvx ruff check
uvx ruff format
uvx isort
uv run pyrefly
```

All four will automatically look for the configuration in the `pyproject.toml`
of the project, as long as you run these commands from somewhere within the
project directory.

### Branch naming and commit message convention

When you create a new branch to work on your PR, you may choose any name that
is appropriate. If you work on an existing issue, it is recommended that the
branch name start with the number of the issue. The shorter you can make the
name, the better.

Commit messages must describe the changes made in the commit in one line. The
line does not need to have a specific format, but it should not exceed 70
characters in length. Write in plain ASCII, avoid special characters or emojis.
The message should be capable of identifying your changes, as in: If a maintainer
ever looks for a commit that changed a feature, the commit that did it must be
recognizable by just its message. Should you require more space to explain your
changes in more detail, summarize them as best as you can in one line, then
leave a blank line, and write a longer section below that.

Your PR title should summarize all the work that you have done, similar to a
commit message. This is done as your PR will likely be squashed into a single
commit, and its title will appear as the commit message of the squash-commit.
Again, use the body text of the PR to provide additional information on the
changes, if necessary. You may also use the body of the PR to walk reviewers
through your changes and how to best review the PR.

### Coding conventions

To have your PR accepted, you must adhere to the coding conventions of `pebbledoc`:

- All code must be capable of running on Python 3.13 or later. You may freely
  use any language features introduced in 3.13 or before, but not later.
- All code must be fully typed and must pass type checking. Take `pyrefly`
  warnings serious and fix your typing when they occur.
- `pebbledoc` enforces a maximum code complexity via `ruff`. Make sure your
  functions and classes have clear, focused responsibilities.
- Disabling linting, formatting, or type checking must only be done in cases
  where it is better for maintainability or readability, or in places where it
  is simply unavoidable. You will be asked to justify all directives where it
  is not immediately clear this is the case.
- All members (classes, modules, functions, methods, etc.) must be documented
  with a complete docstring. See [below](#documentation-conventions) for details.
- All new code must be covered by both unit and acceptance tests. See [below](#testing-conventions)
  for details.

### Testing conventions

You can run the test suite for `pebbledoc` using

```bash
uv run pytest ./tests/
```

from the project root. All new code must be covered by unit tests, and new
features must additionally be covered by acceptance tests. `pebbledoc` uses
`pytest` for all its tests.

Unit tests must test only single logical units. Everything else must be patched
or mocked using `pytest-mock`. Any interactions with the file system in the
code under test **must** be mocked as well. Private functions or methods do not
need to be covered by unit tests, but they can be covered if you deem it sensible.
For example, the various `_member_*` functions of the `inspect_runtime.py`
module are all covered by unit tests, despite being marked as private. This is
done since they cover a large part of the logic of the module, and testing only
the public `markdown_documentation` function would not have provided the
granularity needed to quickly spot regressions. Use your best judgment for what
private members require unit test coverage.

Acceptance tests are meant to prove that `pebbledoc` works end-to-end. They
mimic user interaction by providing faux user input and inspecting the output
that would have been written to file by `pebbledoc`. If you implement a new
feature, you must also provide an acceptance test that tests this feature. If
you only provide a new RST syntax support, you must add this syntax to the
existing acceptance tests.

### Documentation conventions

As stated before, all members of `pebbledoc` must have a docstring. Of course,
`pebbledoc` uses the RST format for its docstrings. Modules and test functions
can have only a single line, providing a brief description. Functions, classes,
and methods however must have more verbose docstrings. Class docstrings must
provide an explanation for the class's purpose and how to use it, while function
and method docstrings must additionally document the behavior, the parameters,
return values, and exceptions that may be raised by them. The docstrings of
private members should be aimed at other developers, while the docstrings of
public members should be aimed at users.

When you add support for a new Sphinx-specific RST syntax feature, you should
add a note to the README of the project in the respective section. Additionally,
whenever you implement support for a new RST syntax feature, you must update
the [FEATURES.md](./FEATURES.md) document accordingly.

Finally, all changes you make must be documented in the [CHANGELOG](./CHANGELOG.md)
of the project. `pebbledoc` uses the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
format for its changelog. Your additions to it must adhere to this format as
well. PRs without an updated CHANGELOG cannot be accepted.

## Disclaimer about rejections

The maintainers of `pebbledoc` reserve the right to reject contributions that
are not adhering to this contributing guide, the code of conduct, or the quality
standards of `pebbledoc`. Furthermore, contributions that are too large in scope
to be reasonably reviewed by a single human will also be rejected.

Additionally, the maintainers reserve the right to reject unsolicited PRs if
the provided changes are not aligning with the purpose or future direction of
the `pebbledoc` project.

All PRs that merely fix change whitespaces, fix some typos, fix formatting, etc.
without substantive impact (i.e. fixing factually wrong wording, removing
ambiguity, or fixing incorrect rendering) will be rejected.
