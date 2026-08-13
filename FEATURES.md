# Supported RST features

This document lists all features of the RST markup language and the additional
features supported by the Sphinx documentation tool and shows whether they are
currently supported by `pebbledoc`. The document uses four icons to quickly
show support status for each feature:

| Icon               | Meaning                                         |
|--------------------|-------------------------------------------------|
| :white_check_mark: | Feature is fully supported                      |
| :yellow_circle:    | Feature is partially or conditionally supported |
| :soon:             | Feature is planned and will be supported soon   |
| :x:                | Feature is not and will not be supported        |
| :grey_question:    | Support is uncertain and hasn't been tested     |

For an explanation and examples of each listed feature, see the [RST Quick Reference](https://docutils.sourceforge.io/docs/user/rst/quickref.html).


## RST features

### Inline markup

| Feature                             | Status             | Note                          |
|-------------------------------------|--------------------|-------------------------------|
| `*emphasis*`                        | :white_check_mark: |                               |
| `**strong emphasis**`               | :white_check_mark: |                               |
| `` `interpreted text` ``            | :white_check_mark: | Interpreted as inline literal |
| ` ``inline literal`` `              | :white_check_mark: |                               |
| `reference_`                        | :white_check_mark: |                               |
| `` `phrase reference`_ ``           | :white_check_mark: |                               |
| `` `anonymous`__ ``                 | :grey_question:    |                               |
| `` _`inline literal target` ``      | :grey_question:    |                               |
| `\| substitution reference \|`      | :x:                |                               |
| `footnote reference [1]_`           | :soon:             |                               |
| `citation reference [CIT2026]_`     | :soon:             |                               |
| Direct links (`https://github.com`) | :white_check_mark: |                               |

### Document structure

Headers inside docstrings are generally not supported by `pebbledoc`, as it must
control headers itself.

| Feature           | Status          | Note                                                                 |
|-------------------|-----------------|----------------------------------------------------------------------|
| Headers           | :x:             |                                                                      |
| Transitions       | :grey_question: |                                                                      |
| Table of contents | :x:             | From directive `.. contents::`; TOC is managed by `pebbledoc` itself |

### Lists

| Feature                 | Status             | Note                                                                                  |
|-------------------------|--------------------|---------------------------------------------------------------------------------------|
| Bullet lists            | :white_check_mark: | Bullets must be `-`, `+`, or `*`                                                      |
| Nested bullet lists     | :white_check_mark: |                                                                                       |
| Enumerated lists        | :white_check_mark: | Including lists not starting at 1                                                     |
| Nested enumerated lists | :white_check_mark: |                                                                                       |
| Mixed nested lists      | :white_check_mark: |                                                                                       |
| Definition lists        | :soon:             |                                                                                       |
| Field lists             | :white_check_mark: | Including support for function parameter field lists ([see below](#info-field-lists)) |
| Option lists            | :x:                |                                                                                       |

### Blocks

| Feature                 | Status             | Note                   |
|-------------------------|--------------------|------------------------|
| Literal blocks (`::`)   | :white_check_mark: |                        |
| Line blocks (`\|`)      | :soon:             |                        |
| Block quotes            | :white_check_mark: | Including attributions |
| Docstest blocks (`>>>`) | :white_check_mark: |                        |

### Tables

| Feature      | Status | Note                                                               |
|--------------|--------|--------------------------------------------------------------------|
| Grid table   | :soon: | Markdown table syntax allows only a subset of RST table structures |
| Simple table | :soon: |                                                                    |
| CSV table    | :x:    | From directive `.. csv-table::`                                    |
| List table   | :soon: | From directive `.. list-table::`                                   |

### Footnotes

| Feature                          | Status | Note |
|----------------------------------|--------|------|
| Numbered footnotes (`[5]_`)      | :soon: |      |
| Auto-numbered footnotes (`[#]_`) | :soon: |      |
| Auto-number labels (`[#first]_`) | :soon: |      |
| Auto-symbol footnotes (`[*]_`)   | :soon: |      |

### Directives

| Feature                                      | Status             | Note                                                                                            |
|----------------------------------------------|--------------------|-------------------------------------------------------------------------------------------------|
| Admonitions (e.g. `.. note::`)               | :white_check_mark: | Admonitions not supported as GitHub alerts are managed via the `admonition_style` config option |
| Generic admonition (`.. admonition::`)       | :white_check_mark: |                                                                                                 |
| Images (`.. image::`)                        | :soon:             |                                                                                                 |
| Figures (`.. figure::`)                      | :x:                |                                                                                                 |
| Topic (`.. topic::`)                         | :soon:             |                                                                                                 |
| Sidebar (`.. sidebar::`                      | :soon:             |                                                                                                 |
| Parsed literal block (`.. parsed-literal::`) | :grey_question:    |                                                                                                 |
| Code block (`.. code::`)                     | :white_check_mark: | Sphinx version `.. code-block::` is also supported                                              |
| Math block (`.. math::`)                     | :white_check_mark: |                                                                                                 |
| Rubric (`.. rubric::`)                       | :soon:             |                                                                                                 |
| Epigraph (`.. epigraph::`)                   | :grey_question:    |                                                                                                 |
| Highlights (`.. highlights::`)               | :grey_question:    |                                                                                                 |
| Pull-Quote (`.. pull-quote::`)               | :grey_question:    |                                                                                                 |
| Compound paragraph (`.. compound::`)         | :x:                |                                                                                                 |
| Container                                    | :yellow_circle:    | Containers are ignored                                                                          |


### Roles

| Feature                 | Status             | Note                   |
|-------------------------|--------------------|------------------------|
| `:abbreviation:`        | :yellow_circle:    | Rendered as plain text |
| `:acronym:`             | :yellow_circle:    | Rendered as plain text |
| `:code:`                | :white_check_mark: |                        |
| `:emphasis`             | :white_check_mark: |                        |
| `:literal:`             | :white_check_mark: |                        |
| `:math:`                | :white_check_mark: |                        |
| `:PEP:` (PEP reference) | :soon:             |                        |
| `:RFC:` (RFC reference) | :x:                |                        |
| `:strong:`              | :white_check_mark: |                        |
| `:subscript:`           | :white_check_mark: |                        |
| `:superscript:`         | :white_check_mark: |                        |
| `:title:`               | :yellow_circle:    | Rendered as plain text |
| `:raw:`                 | :x:                |                        |

### Comments

| Feature        | Status             | Note |
|----------------|--------------------|------|
| Comment (`..`) | :white_check_mark: |      |


## Sphinx features

In addition to the standard docutils RST syntax, Sphinx allows for some additional
syntax, such as more directives, roles, and reference types. This section lists
support for these features.

### Roles

Most of these roles are meant to create documentation pages and are unlikely
to be used in docstrings. Hence, most are unsupported.

| Feature           | Status | Note                                                                              |
|-------------------|--------|-----------------------------------------------------------------------------------|
| `:any:`           | :x:    |                                                                                   |
| `:doc:`           | :x:    | `pebbledoc` only renders one document; links to other documents are not supported |
| `:download:`      | :x:    |                                                                                   |
| `:confval:`       | :x:    |                                                                                   |
| `:envvar:`        | :x:    |                                                                                   |
| `:keyword:`       | :x:    |                                                                                   |
| `:numref:`        | :x:    |                                                                                   |
| `:option:`        | :x:    |                                                                                   |
| `:ref:`           | :soon: |                                                                                   |
| `:term:`          | :x:    |                                                                                   |
| `:token:`         | :x:    |                                                                                   |
| `:eq:`            | :x:    |                                                                                   |
| `:abbr:`          | :x:    |                                                                                   |
| `:command:`       | :x:    |                                                                                   |
| `:dfn:`           | :x:    |                                                                                   |
| `:file:`          | :x:    |                                                                                   |
| `:guilabel:`      | :x:    |                                                                                   |
| `:kbd:`           | :soon: |                                                                                   |
| `:mailheader:`    | :x:    |                                                                                   |
| `:makevar:`       | :x:    |                                                                                   |
| `:manpage:`       | :x:    |                                                                                   |
| `:menuselection:` | :x:    |                                                                                   |
| `:mimetype:`      | :x:    |                                                                                   |
| `:newsgroup:`     | :x:    |                                                                                   |
| `:program:`       | :x:    |                                                                                   |
| `:regexp:`        | :x:    |                                                                                   |
| `:samp:`          | :x:    |                                                                                   |
| `:cve:`           | :x:    |                                                                                   |
| `:cwe:`           | :x:    |                                                                                   |

### Substitutions

| Feature                    | Status | Note |
|----------------------------|--------|------|
| `\|release\|`              | :x:    |      |
| `\|version\|`              | :x:    |      |
| `\|today\|`                | :x:    |      |
| `\|translation progress\|` | :x:    |      |

### Directives

| Feature                   | Status             | Name                                               |
|---------------------------|--------------------|----------------------------------------------------|
| `.. toctree::`            | :x:                | TOC trees are directly controlled by `pebbledoc`   |
| `.. seealso::`            | :soon:             | Sphinx-specific admonition                         |
| `.. version-added::`      | :white_check_mark: | Includes custom rendering as block quote with icon |
| `.. versionadded::`       | :white_check_mark: | Includes custom rendering as block quote with icon |
| `.. version-changed::`    | :white_check_mark: | Includes custom rendering as block quote with icon |
| `.. versionchanged::`     | :white_check_mark: | Includes custom rendering as block quote with icon |
| `.. version-deprecated::` | :white_check_mark: | Includes custom rendering as block quote with icon |
| `.. deprecated::`         | :white_check_mark: | Includes custom rendering as block quote with icon |
| `.. version-removed::`    | :white_check_mark: | Includes custom rendering as block quote with icon |
| `.. versionremoved::`     | :white_check_mark: | Includes custom rendering as block quote with icon |
| `.. centered::`           | :soon:             |                                                    |
| `.. hlist::`              | :x:                |                                                    |
| `.. highlight::`          | :soon:             |                                                    |
| `.. code-block::`         | :white_check_mark: |                                                    |
| `.. sourcecode::`         | :grey_question:    |                                                    |
| `.. literalinclude::`     | :x:                |                                                    |
| `.. glossary::`           | :x:                |                                                    |
| `.. sectionauthor::`      | :x:                |                                                    |
| `.. codeauthor::`         | :x:                |                                                    |
| `.. index::`              | :x:                |                                                    |
| `.. only::`               | :x:                |                                                    |
| `.. tabularcolumns::`     | :x:                |                                                    |
| `.. productionlist::`     | :x:                |                                                    |

### Cross-references and domains

`pebbledoc` assumes the standard domain to be the Python domain. Python is the
only supported domain as of now; references to other domains are not supported.
As such, `pebbledoc` assumes all roles to drop the prefix `:py`.

Out of the Python domain, the following reference types are supported:

| Feature   | Status          | Note                                                                                                                          |
|-----------|-----------------|-------------------------------------------------------------------------------------------------------------------------------|
| `:mod:`   | :yellow_circle: | Reference target must be importable name (optionally with prefixes removed); module must be in documentation as well          |
| `:func:`  | :yellow_circle: | Reference target must be importable name (optionally with prefixes removed); function must be in documentation as well        |
| `:deco:`  | :yellow_circle: | Reference target must be importable name (optionally with prefixes removed); decorator must be in documentation as well       |
| `:data:`  | :yellow_circle: | Reference target must be importable name (optionally with prefixes removed); variable must be in documentation as well        |
| `:const:` | :yellow_circle: | Reference target must be importable name (optionally with prefixes removed); constant must be in documentation as well        |
| `:class:` | :yellow_circle: | Reference target must be importable name (optionally with prefixes removed); class must be in documentation as well           |
| `:meth:`  | :yellow_circle: | Reference target must be importable name (optionally with prefixes removed); method must be in documentation as well          |
| `:attr:`  | :yellow_circle: | Attributes are not included in the documentation, unless they are properties                                                  |
| `:type:`  | :yellow_circle: | Reference target must be importable name (optionally with prefixes removed); type must be in documentation as well            |
| `:exc:`   | :yellow_circle: | Reference target must be importable name (optionally with prefixes removed); exception class must be in documentation as well |
| `:obj:`   | :yellow_circle: | Reference target must be importable name (optionally with prefixes removed); object must be in documentation as well          |

References may contain further syntax:

| Feature                                                    | Status             | Note                                                              |
|------------------------------------------------------------|--------------------|-------------------------------------------------------------------|
| Custom link text (e.g. `` :role:`custom text <target>` ``) | :white_check_mark: |                                                                   |
| Suppressed link (`!` prefix)                               | :white_check_mark: | Reference renders as plain inline literal instead                 |
| Shortened name (`~` prefix)                                | :white_check_mark: | Does not affect target (i.e. target name remains fully qualified) |

### Manual member documentation directives

The Python domain provides directives to mark documentation for Python members.
As `pebbledoc` specializes in *automated* documentation generation (as opposed
to manual documentation), these are not supported.

| Feature                  | Status | Note |
|--------------------------|--------|------|
| `..py:module::`          | :x:    |      |
| `..py:currentmodule::`   | :x:    |      |
| `..py:function::`        | :x:    |      |
| `..py:data::`            | :x:    |      |
| `..py:exception::`       | :x:    |      |
| `..py:class::`           | :x:    |      |
| `..py:attribute::`       | :x:    |      |
| `..py:property::`        | :x:    |      |
| `..py:type::`            | :x:    |      |
| `..py:method::`          | :x:    |      |
| `..py:staticmethod::`    | :x:    |      |
| `..py:classmethod::`     | :x:    |      |
| `..py:decorator::`       | :x:    |      |
| `..py:decoratormethod::` | :x:    |      |

### Info field lists

Within the docstrings of classes, functions, methods, etc. one can use the
following supported field list special field names to invoke special rendering
of the resulting field list. See [Sphinx documentation](https://www.sphinx-doc.org/en/master/usage/domains/python.html#info-field-lists)
of info field lists for more information and examples.

> [!CAUTION]
>
> An info field list may only ever contain a mix of the field names listed in the
> following table, **or** other arbitrary fields. Any field list that mixes the
> following field names with other field names will cause a parsing error when
> attempting to generate documentation.

| Feature       | Status             | Note                                                                |
|---------------|--------------------|---------------------------------------------------------------------|
| `:param:`     | :white_check_mark: |                                                                     |
| `:parameter:` | :soon:             |                                                                     |
| `:arg:`       | :soon:             |                                                                     |
| `:argument:`  | :soon:             |                                                                     |
| `:key:`       | :soon:             |                                                                     |
| `:keyword:`   | :soon:             |                                                                     |
| `:type:`      | :white_check_mark: |                                                                     |
| `:raises:`    | :white_check_mark: |                                                                     |
| `:raise:`     | :white_check_mark: |                                                                     |
| `:except:`    | :soon:             |                                                                     |
| `:exception:` | :soon:             |                                                                     |
| `:var:`       | :soon:             |                                                                     |
| `:ivar:`      | :soon:             |                                                                     |
| `:cvar:`      | :soon:             |                                                                     |
| `:vartype:`   | :soon:             |                                                                     |
| `:return:`    | :white_check_mark: | May appear multiple times                                           |
| `:returns:`   | :white_check_mark: | May appear multiple times                                           |
| `:rtype:`     | :white_check_mark: | May appear only once; last appearance is used otherwise             |
| `:meta:`      | :soon:             | Is ignored, but will cause errors when used in any other field list |
