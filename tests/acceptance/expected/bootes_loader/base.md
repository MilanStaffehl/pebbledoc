# bootes_loader documentation

> #### Table of contents
> - [`bootes_loader`](#bootes_loader)
>   - [`bootes_loader.SUPPORTED_CATALOGS`](#bootes_loadersupported_catalogs)
>   - [`bootes_loader.Catalog`](#bootes_loadercatalog)
>   - [`bootes_loader.load_catalog`](#bootes_loaderload_catalog)


## `bootes_loader`

<sup>[Back to top](#bootes_loader-documentation)</sup>

Bootes is a Python library to help load various halo catalogs.

Note that this is not a real package, and it only exists as fixture for
the `pebbledoc` package. As opposed to `stellarium_lite`, this one
is entirely untyped and relies on docstring for type hints.

> "My disappointment is immeasurable, and my day is ruined."
>
> -- Someone expecting a real halo loading package.

- **author:** Milan Staffehl
- **copyright:** 2026 Milan Staffehl

<a name="supported_catalogs"></a>
### `bootes_loader.SUPPORTED_CATALOGS`

<sup>[Back to top](#bootes_loader-documentation)</sup>

```Python
SUPPORTED_CATALOGS: list = ['AHF', 'FOF', 'ROCKSTAR', 'HBT+', 'HBT-HERONS', 'SUBFIND']
```

<a name="catalog"></a>
### `bootes_loader.Catalog`

<sup>[Back to top](#bootes_loader-documentation)</sup>

```Python
Catalog(ABC)
```

An abstract base class for catalogs.

The class provides abstract methods that implementations for each of
the supported halo catalogs must implement. You can add support for
your own catalog by implementing this abstract base class.

> [!CAUTION]
>
> Any catalog from [`SUPPORTED_CATALOGS`](#supported_catalogs) that does not
> have an associated catalog subclass will cause importing the
> package to raise an exception.

<a name="catalogload_catalog"></a>
<a name="load_catalog"></a>
#### `bootes_loader.Catalog.load_catalog`

<sup>[Back to top](#bootes_loader-documentation)</sup>

```Python
@abstractmethod
Catalog.load_catalog(self, path, structure, snapshot)
```

Function to load the catalog from file.

The function **must** return the full raw file content of the
given snapshot. Fields are filtered only later in the
`extract_fields` method.

**Parameters:**

- `path` (`str | os.PathLike`): Path to the directory of the catalog file.
- `structure` (`str | None`): Structure of the catalog file.
- `snapshot` (`int`): The number of the snapshot.

**Returns:**

`Any`: The full raw file content of the catalog for the given snapshot.

<a name="load_catalog"></a>
### `bootes_loader.load_catalog`

<sup>[Back to top](#bootes_loader-documentation)</sup>

```Python
load_catalog(catalog_name, catalog_type, path, snapshot, fields)
```

Load data from anyone of the supported halo catalogs.

**Parameters:**

- `catalog_name` (`str`): The name of the catalog. Must be one of the supported catalogs. See [`SUPPORTED_CATALOGS`](#supported_catalogs) for options.
- `catalog_type` (`Literal['snapshot', 'merger tree']`): The type of catalog, i.e. the file structure of the catalog files.
- `path` (`str | os.PathLike`): The path to the catalog directory. Must contain the directory or source file for the chosen snapshot.
- `snapshot` (`int`): The snapshot to load.
- `fields` (`list[str]`): A list of fields to load from the catalog. See the documentation for the respective catalog to find supported fields.

**Raises:**

- `KeyError`: When a field was requested that is not supported by the chosen catalog.

**Returns:**

`dict[str, NDArray[Any]]`: A mapping of field names to the respective values as arrays.
