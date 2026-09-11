# bootes_loader

[![PyPI](https://img.shields.io/badge/pypi-not_published-lightgrey)](https://pypi.org)
[![License](https://img.shields.io/badge/license-MIT-blue)](#license)

A **tiny untyped mock astronomy package** used as a test fixture for an
RST-to-Markdown docstring renderer.

> "I cannot believe I fell for this again."
> — someone who already fell for `bootes_loader` in the regular acceptance tests

## Contents

Merely a few mock function, all papier-mâché!

## Installation

This package is not published anywhere. To use it locally:

```bash
git clone https://github.com/example/bootes_loader.git
cd bootes_loader
pip install -e .
```

## Quick example

```python
from bootes_loader import load_catalog

path = "~/storage/simulations/atalea/catalogs/"
fields = ["GroupPos", "Group_M_Crit200"]
catalog_data = load_catalog("ATALEA_catalogs", "SUBFIND", path, 334, fields)
```

## Package Documentation

This section lists the full public API of the `bootes_loader` package.

### `bootes_loader`

Bootes is a Python library to help load various halo catalogs.

Note that this is not a real package, and it only exists as fixture for
the `pebbledoc` package. As opposed to `stellarium_lite`, this one
is entirely untyped and relies on docstring for type hints.

> "My disappointment is immeasurable, and my day is ruined."
>
> -- Someone expecting a real halo loading package.

<sup>[Back to top](#package-documentation)</sup>

<a name="supported_catalogs"></a>
#### `bootes_loader.SUPPORTED_CATALOGS`

```Python
SUPPORTED_CATALOGS: list = ['AHF', 'FOF', 'ROCKSTAR', 'HBT+', 'HBT-HERONS', 'SUBFIND']
```

<sup>[Back to top](#package-documentation)</sup>

<a name="catalog"></a>
#### `bootes_loader.Catalog`

```Python
Catalog(ABC)
```

An abstract base class for catalogs.

The class provides abstract methods that implementations for each of
the supported halo catalogs must implement. You can add support for
your own catalog by implementing this abstract base class.

> [!WARNING]
>
> Any catalog from [`SUPPORTED_CATALOGS`](#supported_catalogs) that does not
> have an associated catalog subclass will cause importing the
> package to raise an exception.

<sup>[Back to top](#package-documentation)</sup>

<a name="catalogload_catalog"></a>
<a name="load_catalog"></a>
##### `bootes_loader.Catalog.load_catalog`

```Python
@abstractmethod
Catalog.load_catalog(self, path, structure, snapshot)
```

Function to load the catalog from file.

The function **must** return the full raw file content of the
given snapshot. Fields are filtered only later in the
`extract_fields` method.

<details open>
<summary><b>Parameters:</b></summary>

- `path` (`str | os.PathLike`): Path to the directory of the catalog file.
- `structure` (`str | None`): Structure of the catalog file.
- `snapshot` (`int`): The number of the snapshot.

</details>

<details open>
<summary><b>Returns:</b></summary>

`Any`: The full raw file content of the catalog for the given snapshot.

</details>

<sup>[Back to top](#package-documentation)</sup>

<a name="load_catalog"></a>
#### `bootes_loader.load_catalog`

```Python
load_catalog(catalog_name, catalog_type, path, snapshot, fields)
```

Load data from anyone of the supported halo catalogs.

<details open>
<summary><b>Parameters:</b></summary>

- `catalog_name` (`str`): The name of the catalog. Must be one of the supported catalogs. See [`SUPPORTED_CATALOGS`](#supported_catalogs) for options.
- `catalog_type` (`Literal['snapshot', 'merger tree']`): The type of catalog, i.e. the file structure of the catalog files.
- `path` (`str | os.PathLike`): The path to the catalog directory. Must contain the directory or source file for the chosen snapshot.
- `snapshot` (`int`): The snapshot to load.
- `fields` (`list[str | None]`): A list of fields to load from the catalog. See the documentation for the respective catalog to find supported fields.

</details>

<details open>
<summary><b>Raises:</b></summary>

- `KeyError`: When a field was requested that is not supported by the chosen catalog.

</details>

<details open>
<summary><b>Returns:</b></summary>

`dict[str, NDArray[Any]]`: A mapping of field names to the respective values as arrays.

</details>

<sup>[Back to top](#package-documentation)</sup>

## Development

Run the test suite with:

```bash
pytest
```

## Caveats

- [ ] No real astronomical data
- [ ] No real math — formulas are illustrative only
- [x] Exists purely to exercise a docstring parser

Don't be that guy from the quote -- don't fall for it, man!

## License

MIT; see `LICENSE` for details.
